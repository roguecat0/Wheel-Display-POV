#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "ArduinoJson.h"
#include "esp_system.h"

const char* ssid = "POV";
const char* password = "";
String header;
AsyncWebServer server(80);    
AsyncWebSocket ws("/ws");

#define SLICES 300
#define LEDS 7
#define BITS 24
#define WAIT 1

#define PIN_MASK 0b11111111111110100 //(GPIO 2,4,5,6,7,8,9,10,11,12,13,14,15,16)
#define CLK_MASK 0b10  //(GPIO 1)

#define START_SLICE 75
volatile unsigned int counter = 0;

volatile uint16_t curr_slice = START_SLICE;

uint32_t image[SLICES][168]; 

void IRAM_ATTR wait_for(int times) {
  for (int i = 0; i < times; i++) {
    asm("nop;");
  }
}

void IRAM_ATTR draw_leds() {
    REG_WRITE(GPIO_OUT_W1TC_REG, PIN_MASK);
    for (int j = 0; j < 32; j++) {            //start frame
      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);
    }

    for (int j = 0; j < LEDS; j++) { 
                                              //intenciteit instellen
      REG_WRITE(GPIO_OUT_W1TS_REG, PIN_MASK); //1 * 3

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TC_REG, PIN_MASK); //0 * 2

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TS_REG, PIN_MASK); //1 * 2
      
      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);

      //REG_WRITE(GPIO_OUT_W1TC_REG, PIN_MASK); //0

      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);


      for(int k = 0; k < BITS; k++){             // verzenden kleuren
        REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
        REG_WRITE(GPIO_OUT_W1TC_REG, PIN_MASK);
        REG_WRITE(GPIO_OUT_W1TS_REG, PIN_MASK & image[curr_slice][j*BITS + k]);
        wait_for(WAIT);
        REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
        wait_for(WAIT);
      }
    }

    REG_WRITE(GPIO_OUT_W1TS_REG, PIN_MASK);  //eind frame
    for (int j = 0; j < 32; j++) {
      REG_WRITE(GPIO_OUT_W1TC_REG, CLK_MASK);
      wait_for(WAIT);
      REG_WRITE(GPIO_OUT_W1TS_REG, CLK_MASK);
      wait_for(WAIT);
    }
  curr_slice++;
  curr_slice %= SLICES;
  counter++;
}


uint64_t alarmTime = 1000;
hw_timer_t * timer1 = NULL;
hw_timer_t * timer2 = NULL;

void IRAM_ATTR calculate_time(){
  if(counter >= 20){
    uint64_t new_time = timerRead(timer1);
    timerRestart(timer1);
    timerAlarmWrite(timer2, new_time/SLICES, true);
    curr_slice = START_SLICE;
    counter = 0;
  }
}


void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {  //verwerken websocket bericht
  const size_t capacity = len;
  DynamicJsonBuffer jsonBuffer(capacity);
  JsonObject& parsed = jsonBuffer.parseObject((char*) data);
  for (auto keyValue : parsed){
    int cur_slice = atoi(keyValue.key);
    for (int i= 0; i<LEDS * BITS; i++) {
      image[cur_slice][i] = parsed[keyValue.key][i];      
    }
  }
}


void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type, void *arg, uint8_t *data, size_t len) { //verwerken besocket event
  detachInterrupt(digitalPinToInterrupt(17));
  switch (type) {
    case WS_EVT_CONNECT:
      break;
    case WS_EVT_DISCONNECT:
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len );
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
  ws.cleanupClients();
  attachInterrupt(17, calculate_time, FALLING);
}

void  initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

void setup() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  initWebSocket();
  server.begin();
  
  timer1 = timerBegin(1, 400, true);
  timer2 = timerBegin(2, 400, true);
  timerAttachInterrupt(timer2, &draw_leds, true);
  timerAlarmWrite(timer2, alarmTime, true);
  timerAlarmEnable(timer2);
  
  REG_WRITE(GPIO_ENABLE_REG, PIN_MASK | CLK_MASK);
  delay(1000);
  pinMode(17, INPUT_PULLUP);
  attachInterrupt(17, calculate_time, FALLING);
}

void loop(){
}

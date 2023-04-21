// Load libraries
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include "FS.h"
#include "SPIFFS.h"
#include "ArduinoJson.h"
//to format SPIFFS, only needs to be done once, after that it can be put on false
#define FORMAT_SPIFFS_IF_FAILED false

/*********
  general part
*********/
const int serieleds = 1;
const int leds = 24;
const int slices = 50;
long gegevens[slices][serieleds * leds] = 1;

/*********
  SPIFFS part
*********/

//read file function
void readFile(fs::FS &fs, const char * path) {
  Serial.printf("Reading file: %s\r\n", path);

  File file = fs.open(path);
  if (!file || file.isDirectory()) {
    Serial.println("- failed to open file for reading");
    return;
  }
  Serial.println("- read from file:");
  while (file.available()) {
    Serial.write(file.read());
  }
}

/*********
  Wi-Fi part
*********/

//network credentials
const char* ssid = "esp32";
const char* password = "";
// Set server port number
// Variable for HTTP request
String header;

/*********
  Websocket part
*********/

AsyncWebServer server(80);    
AsyncWebSocket ws("/ws");

void notifyClients() {
  ws.textAll("hallo daar");
}

void printArray( const long a[][ serieleds * leds ] ) {
   // loop through array's slices
   for ( int i = 0; i < slices; ++i ) {
      // loop through leds of current row
      for ( int j = 0; j < serieleds *leds; ++j ) {
      Serial.print (a[ i ][ j ] );
      Serial.print(",");
      }
      Serial.print("\n" ) ; // start new line of output
   } 
}

void handleWebSocketMessage(void *arg, uint8_t *data, size_t len) {
  const size_t capacity = len;
  DynamicJsonBuffer jsonBuffer(capacity);
  JsonObject& parsed = jsonBuffer.parseObject((char*) data);
  for (auto keyValue : parsed){
    int cur_slice = atoi(keyValue.key);
    for (int i= 0; i<serieleds *leds; i++) {
      gegevens[cur_slice][i] = parsed[keyValue.key][i];
      //Serial.printf("\n");
      
    }
    //keyValue.value.printTo(Serial);
  }
  //Serial.println((char*) data);
  //Serial.println("------------------------");
  //parsed.printTo(Serial);
  
}

void onEvent(AsyncWebSocket *server, AsyncWebSocketClient *client, AwsEventType type,
             void *arg, uint8_t *data, size_t len) {
  switch (type) {
    case WS_EVT_CONNECT:
      Serial.printf("WebSocket client #%u connected from %s\n", client->id(), client->remoteIP().toString().c_str());
      break;
    case WS_EVT_DISCONNECT:
      Serial.printf("WebSocket client #%u disconnected\n", client->id());
      printArray(gegevens);
      break;
    case WS_EVT_DATA:
      handleWebSocketMessage(arg, data, len );
      break;
    case WS_EVT_PONG:
    case WS_EVT_ERROR:
      break;
  }
}

void initWebSocket() {
  ws.onEvent(onEvent);
  server.addHandler(&ws);
}

String processor(const String& var){
  Serial.println(var);
  return String();
}

void setup() {
  // setup code to run once:
  // start communication and set baud rate
  Serial.begin(115200);
  /*********
    Wi-Fi part
  *********/
  // set up Wi-Fi acces-point
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  Serial.print("Acces-point with IP: ");
  IPAddress IP = WiFi.softAPIP();
  Serial.println(IP);
  /*********
    SPIFFS part
  *********/
  //mount the file system, this only has to be done the first time
  if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }

  initWebSocket();

  // Start server
  server.begin();
  
}

void loop() {
  // main code here to run repeatedly:
  ws.cleanupClients();
}

// Load libraries
#include <WiFi.h>
#include <ArduinoJson.h>
#include "FS.h"
#include "SPIFFS.h"
//to format SPIFFS, only needs to be done once, after that it can be put on false
#define FORMAT_SPIFFS_IF_FAILED true




/*********
  general part
*********/

StaticJsonBuffer<200> jsonBuffer;     //TODO: CHANGE TO RIGHT SIZE WHEN I KNOW IT

void SaveJSONData(String header) {
  Serial.println("the command send is: " + header);
  header.remove(0, 20);
  JsonObject& root = jsonBuffer.parseObject(header);
  if(!root.success()) {
    Serial.println("parseObject() failed");
    return false;
  }
  else {
    
  }
  
}
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
const char* ssid = "de_betere_esp";
const char* password = "beterdanhelpendehand";
// Set server port number
WiFiServer server(80);
// Variable for HTTP request
String header;



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
  server.begin();
  /*********
    SPIFFS part
  *********/
  //mount the file system, this only has to be done the first time
  if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }
}

void loop() {
  // main code here to run repeatedly:
  /*********
    Wi-Fi part
  *********/
  WiFiClient client = server.available();
  if (client) { 
    Serial.println("New Client.");
    String incommingData = "";    //string to hold incoming data
    //read available data from client when it's connected
    header = "";
    while (client.connected()) {
      if (client.available()) {
        char c = client.read();
        header += c;        //add the data to the header
        if (c == '\n') {    //check for newline
          if (incommingData.length() == 0) {  //blank after newline -> end of HTTP request
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println(); 
            if (header.indexOf("POST /echo/post/json") >= 0){   //TEVON MOET ANTWOORDEN DIE KLOOTZAK
              SaveJSONData(header);
            } 
             client.println();  //another blank line to end http
            break;
          } 
          else { // if you got a newline, then clear currentLine
            incommingData = "";
          }
        } 
        else if (c != '\r') {  // if you got anything else but a carriage return character,
          incommingData += c;      // add it to the end of the currentLine
        }
  
      }
      
    }
    
    client.stop();
    Serial.println("Client disconnected."); 
  }
}

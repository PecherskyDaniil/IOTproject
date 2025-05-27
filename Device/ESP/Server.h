#include <ESP8266WebServer.h>
#include "EEPROM.h"
ESP8266WebServer server(80);    



void handleRoot() {                         
  server.send(200, 
              "text/html", 
              "<div><form style=\"width:fit-content;margin-left: auto; margin-right:auto;margin-top:30px;\" action=\"/login\" method=\"POST\">WifiName <input type=\"text\" name=\"wifi_name\"/><br/>Password <input type=\"password\" name=\"wifi_password\"/><br/><input style='font-size=50px' type=\"submit\"></form></div>");
}

void handleLED() {                          
  digitalWrite(led, !digitalRead(led));
  server.sendHeader("Location","/"); // redirection to keep button on the screen
  server.send(303);
}
void handleLogin() {                          
  String message = "Data was recieved";
  EEPROM.begin(100);
  ssidCLI=server.arg("wifi_name");
  Serial.println("Writed "+ssidCLI);
  passwordCLI=server.arg("wifi_password");
  writeStringToEEPROM(0,ssidCLI);
  writeStringToEEPROM(ssidCLI.length()+1,passwordCLI);
  EEPROM.commit();
  server.send(200, "text/plain", message);       //Response to the HTTP request
}

void handleNotFound(){
  server.send(404, "text/plain", "404: Not found"); 
}

void server_init() {
  server.on("/", HTTP_GET, handleRoot);     
  server.on("/login", handleLogin);
  server.onNotFound(handleNotFound);        

  server.begin();                          
  Serial.println("HTTP server started");    
}
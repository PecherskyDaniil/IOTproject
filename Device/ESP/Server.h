#include <ESP8266WebServer.h>
#include "EEPROM.h"
ESP8266WebServer server(80);    



void handleRoot() {                         
  server.send(200, 
              "text/html", 
              "<head><meta charset=\"UTF-8\" /><title>Настройка Wi-Fi</title></head><div style=\"display:flex; justify-content:center; margin-top:30px;\"><form style=\"width: fit-content; padding: 20px; background-color: #e0f7fa; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); display: flex; flex-direction: column; gap: 15px;\" action=\"/login\" method=\"POST\"><h2 style=\"text-align:center; color:#00796b;\">Настройка Wi-Fi</h2><label style=\"font-weight:bold; color:#004d40;\">WifiName</label><input type=\"text\" name=\"wifi_name\" style=\"padding:10px; border-radius:8px; border:1px solid #b2dfdb; font-size:16px; width:250px;\" required/><label style=\"font-weight:bold; color:#004d40;\">Password</label><input type=\"password\" name=\"wifi_password\" style=\"padding:10px; border-radius:8px; border:1px solid #b2dfdb; font-size:16px; width:250px;\" required/><button type=\"submit\" style=\"margin-top:10px; padding:12px; font-size:16px; background-color:#00796b; color:#fff; border:none; border-radius:8px; cursor:pointer; transition:.3s background-color ease-in-out;\">Подключить</button></form></div>");
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
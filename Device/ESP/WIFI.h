#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266WiFiMulti.h>

ESP8266WiFiMulti wifiMulti;    
WiFiClient wifiClient;

String ip = "192.168.4.1"; 

String id(){
  uint8_t mac[WL_MAC_ADDR_LENGTH];
  WiFi.softAPmacAddress(mac);
  String macID = String(mac[WL_MAC_ADDR_LENGTH - 2], HEX) + String(mac[WL_MAC_ADDR_LENGTH - 1], HEX);
  macID.toUpperCase();
  return macID;
}

bool StartAPMode() {
  IPAddress apIP(192, 168, 4, 1);
  WiFi.disconnect();
  WiFi.mode(WIFI_AP);
  WiFi.softAPConfig(apIP, apIP, IPAddress(255, 255, 255, 0));
  WiFi.softAP(ssidAP, passwordAP.c_str());
  Serial.println("");
  Serial.println("WiFi up in AP mode with name: "+ ssidAP);
  return true;
}

bool StartCLIMode() {
  wifiMulti.cleanAPlist();
  wifiMulti.addAP(ssidCLI.c_str(), passwordCLI.c_str());
  //it is possible to add more networks to connect
  int ctries=0;
  wifiMulti.run();
  while(WiFi.status() != WL_CONNECTED && ctries<2) {
      ctries+=1;
      Serial.println("Not connected");
      delay(100);
  }
  if (ctries>=2){
    return false;
  }else{
    WiFi.softAPdisconnect(true);
    return true;
  }
}

bool WIFI_init(bool mode_ap) {
    bool result=false;
    if (mode_ap) {
      StartAPMode();
      ip = WiFi.softAPIP().toString();
      result = true;
    } else {
      result=StartCLIMode();
      ip = WiFi.localIP().toString();
    }
    WiFi.setSleep(false);
    return result;
    //Serial.println("IP address: ");
    //Serial.println(ip);  
}

#include "Config.h"
#include "WIFI.h"
#include "Server.h"
#include "MQTT.h"
#include <ESP8266HTTPClient.h>

bool constat=false;
bool is_sended=false;
long last_sensors_check=millis();
void setup(void){
  Serial.begin(115200);
  EEPROM.begin(100);
  pinMode(led, OUTPUT);
  WIFI_init(true);
  server_init();
  ssidCLI=readStringFromEEPROM(0);
  passwordCLI=readStringFromEEPROM(ssidCLI.length()+1);
  Serial.println(readStringFromEEPROM(ssidCLI.length()+passwordCLI.length()+2));
  feed_hours=readStringFromEEPROM(ssidCLI.length()+passwordCLI.length()+2).toInt();
  if (feed_hours==0){
    feed_hours=100;
  }
  Serial.println(feed_hours);
  Serial.println("eeprom_id: "+ssidCLI);
  Serial.println("eeprom_pass: "+passwordCLI);
  changeMode("APmode");
}
void loop(void){
  if (WiFi.status() == WL_CONNECTED && millis()-last_sensors_check>sensors_check_time){
    Serial.println("s");
    last_sensors_check=millis();
    sensors_check_time=30*60*1000;
  }
  check_and_feed(millis());
  Indicator(indstate);
  if (ssidCLI.length()!=0 && passwordCLI.length()!=0 && !constat){
    if (WIFI_init(false)){
      changeMode("CLImode");
      MQTT_init("/pech/esplamp/stream");
      mqtt_cli.subscribe("/pech/esplamp/123",0);
      constat=true;
    }else{
      Serial.println("Clered eeprom");
      changeMode("APmode");
      clearEEPROM();
      EEPROM.commit();
      ssidCLI = "";
      passwordCLI = "";
      WIFI_init(true);
      server_init();
    }
  }else{
    server.handleClient();
    if (Serial.available()) {
    String inputData = Serial.readStringUntil('\n'); // Читаем строку до символа новой строки
    if (inputData.indexOf("level")>=0){
      if (WiFi.status() == WL_CONNECTED) { // Проверяем подключение к Wi-Fi
        HTTPClient http;
        WiFiClient wifiClient;
        String sendUrl = "http://"+serverIP+"/api/devices/alarm";
        http.begin(wifiClient,sendUrl.c_str()); // Указываем URL
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode=0;
        if (inputData.indexOf("water")>=0){
          httpResponseCode = http.POST("{\"hash\":\""+hash+"\",\"message\":\"Low water level\"}");
        }else{
          httpResponseCode = http.POST("{\"hash\":\""+hash+"\",\"message\":\"High turbidity level\"}");
        }
        
        Serial.println("{\"hash\":\"123\",\"message\":\""+inputData+"\"}");
        Serial.println(httpResponseCode);
      }
    }else{
      int startIndex = 0;
      int spaceIndex = inputData.indexOf(' '); // Находим первый пробел
      String words[2];
      int wordcount=0;
      while (spaceIndex >= 0) {
        String word = inputData.substring(startIndex, spaceIndex); // Извлекаем слово
        words[wordcount]=word; // Выводим слово
        wordcount++;
        startIndex = spaceIndex + 1; // Обновляем начальный индекс для следующего слова
        spaceIndex = inputData.indexOf(' ', startIndex); // Ищем следующий пробел
      }
      String lastWord = inputData.substring(startIndex);
      if (lastWord.length() > 0 && wordcount < 2) {
        words[wordcount] = lastWord; // Добавляем последнее слово в массив
        wordcount++; // Увеличиваем счетчик слов
      }
      // Отправка POST-запроса
      if (WiFi.status() == WL_CONNECTED) { // Проверяем подключение к Wi-Fi
        HTTPClient http;
        WiFiClient wifiClient;
        String sendUrl = "http://"+serverIP+"/api/devices/data/update";
        http.begin(wifiClient,sendUrl.c_str()); // Указываем URL
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST("{\"hash\":\""+hash+"\",\"turbidity\":"+words[0]+",\"waterlevel\":"+words[1]+"}");
        Serial.println("{\"hash\":\""+hash+"\",\"turbidity\":"+words[0]+".0,\"waterlevel\":"+words[1]+".0}");
        Serial.println(httpResponseCode);
      }
    }
    }
  }
  if (WiFi.status() != WL_CONNECTED && constat){
      changeMode("APmode");
      ledstate=0;
      ssidCLI = "";
      passwordCLI = "";
      WIFI_init(true);
      server_init();
      constat=false;
  }
  if (constat){
    //mqtt_cli.publish("/pech/esplamp/hello","hello");
    //Serial.println("hello");
    mqtt_cli.loop();
  }
  //if (topicval.length()==0){// || topicmin.length()==0 || topicmax.length()==0){
  //  get_topics();
  //}else{
  //  if (constat){
  //    mqtt_cli.loop();
  //  }else{
  //    start_serv();
  //  }
  //}
}
void start_serv(){
  WIFI_init(false);
  Serial.println("lol");
  MQTT_init(topicval);
  mqtt_cli.subscribe(topicval.c_str(),0);
  //mqtt_cli.subscribe(topicmin.c_str());
  //mqtt_cli.subscribe(topicmax.c_str());
  constat=true;
}
void get_topics(){
  if (topicval.length()==0){
    Serial.println("Input topic for commands:");
  }//else if (topicmin.length()==0){
  //  Serial.println("Input topic for min values:");
  //}else if (topicmax.length()==0){
  //  Serial.println("Input topic for max values:");
  //}
  if(Serial.available()>0){
    String top = Serial.readString();
    Serial.println(top);
    if (topicval.length()==0 ){
      topicval=top;
    }//else if (topicmin.length()==0 ){
    //  topicmin=top;
    //}else if (topicmax.length()==0 ){
    //  topicmax=top;
    //}
  }
}
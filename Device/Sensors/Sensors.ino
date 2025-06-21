#define WATER_SENSOR A1
#define MUTNO_SENSOR A5
#define MOTOR 12
#include <SoftwareSerial.h>
SoftwareSerial espSerial(8, 9);
void setup() {
  // put your setup code here, to run once:
  pinMode(MOTOR, OUTPUT);
  Serial.begin(9600);
  digitalWrite(MOTOR,HIGH);
  Serial.println("hello");
  // Инициализация SoftwareSerial для общения с ESP8266
  espSerial.begin(115200); // Скорость передачи данных для ESP8266

  Serial.println("Setup complete. Waiting for messages...");
}
String sensorsig = "s\r";
String feedsig = "f\r";
bool levelislow=false;
bool turbidityishigh=false;
void feed(long time){
  long feedtime=millis();
  Serial.println(feedtime);
  while (millis()-feedtime< time && millis()-feedtime>=0){
    digitalWrite(MOTOR,LOW);
  }
  digitalWrite(MOTOR,HIGH);
}
void loop() {
  int watervalue = analogRead(WATER_SENSOR);
  int mutnovalue = analogRead(MUTNO_SENSOR);
  if (watervalue<100 and !levelislow){
    espSerial.println("Low water level");
    levelislow=true;
  }else if(watervalue>100 and levelislow){
    levelislow=false;
  }
  if (mutnovalue<100 and !turbidityishigh){
    espSerial.println("High turbidity level");
    turbidityishigh=true;
  }if (mutnovalue>100 and turbidityishigh){
    turbidityishigh=false;
  }
  if (espSerial.available()) {
    String message = espSerial.readStringUntil('\n'); // Читаем строку до символа новой строки
    Serial.print("Received from ESP: ");
    Serial.println(message);
    Serial.println((int)message.c_str()[1]);
    if (strcmp(message.c_str(), sensorsig.c_str())==0) {
      espSerial.print(mutnovalue);
      espSerial.print(" ");
      espSerial.println(watervalue);
    }else if (strcmp(message.c_str(), feedsig.c_str())==0){
      Serial.println("fed");
      feed(2000);
    }
    
  }
  
}

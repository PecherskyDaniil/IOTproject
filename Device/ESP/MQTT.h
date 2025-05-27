#include <PubSubClient.h>
#include "IndicatorLed.h"
#include "Feed.h"
PubSubClient mqtt_cli(wifiClient);
int maxv=0;
int minv=0;
char val='0';
String topicval="";
int firstcall=1;
long sensors_check_time=0;
void callback(char *topic, byte *payload, unsigned int length) {
    indstate="off";
    //Serial.print("Message arrived in topic: ");
    //Serial.println(topic);
    Serial.print("Message:");
    String val="";
    for (int i = 0; i < length; i++) {
      val=val+(char)payload[i];
    }
    Serial.println(val);
    int pos=val.indexOf(" ");
    if(val.indexOf("feed") >= 0){
      set_feed_time(val.substring(pos+1, val.length()).toInt());
    }
    if (val.indexOf("sensors")>=0){
      sensors_check_time=0;
    }
    //change_led_state(topic,val);
    //Serial.println("-----------------------");
}

void MQTT_init(String tval){
  changeMode("MQTTmode");
  topicval=tval;
  //topicmin=tmin;
  //topicmax=tmax;
  mqtt_cli.setServer(mqtt_broker, mqtt_port);
  mqtt_cli.setCallback(callback);
  while (!mqtt_cli.connected()) {
      Indicator(indstate);
      String client_id = "esp8266-" + String(WiFi.macAddress());
      Serial.print("The client " + client_id);
      Serial.println(" connects to the public mqtt broker\n");
      if (mqtt_cli.connect(client_id.c_str())){
          changeMode("CLImode");
          Serial.println("MQTT Connected");
      } else {
          Serial.print("failed with state ");
          //Serial.println(mqtt_cli.state());
      }
  }  
}


int feed_hours=100;
long last_feed_time=0;
void set_feed_time(int hours){
  feed_hours=hours;
  writeStringToEEPROM(ssidCLI.length()+passwordCLI.length()+2,String(feed_hours));
  EEPROM.commit();
  Serial.println(readStringFromEEPROM(ssidCLI.length()+passwordCLI.length()+2));
  last_feed_time=millis();
}
void check_and_feed(long time){
  if (time-last_feed_time>feed_hours*1000){
    Serial.println("f");
    last_feed_time=millis();
  }
}
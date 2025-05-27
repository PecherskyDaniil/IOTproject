int ledstate=0;
long ledtime=millis();
long doubleled=millis();
String indstate="";
void Indicator(String indstate){
  if (indstate=="APmode"){
    if (millis()-ledtime>500){
      ledstate=!ledstate;
      ledtime=millis();
    }
  }
  if (indstate=="CLImode"){
    if (millis()-ledtime>2000){
      ledstate=!ledstate;
      ledtime=millis();
      doubleled=1;
    }
    if (millis()-ledtime>250 && doubleled==1){
      ledstate=!ledstate;
      ledtime=millis();
      doubleled=2;
    }
    if (millis()-ledtime>250 && doubleled==2){
      ledstate=!ledstate;
      ledtime=millis();
      doubleled=3;
    }
    if (millis()-ledtime>250 && doubleled==3){
      ledstate=!ledstate;
      ledtime=millis();
      doubleled=0;
    }
  }
  if (indstate=="MQTTmode"){
    if (millis()-ledtime>50){
      ledstate=!ledstate;
      ledtime=millis();
    }
  }
  if (indstate!="off"){
    if (ledstate){
        digitalWrite(led, LOW);
    }else{
        digitalWrite(led, HIGH);
    }
  }
}
void changeMode(String mode){
  indstate=mode;
  ledstate=0;
}
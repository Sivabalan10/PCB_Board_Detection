// Synapse 2.0 ----------REVIEW 1.0

// Turn on servo as well as LED when serial input recived
#include <ESP32Servo.h> 

#define ERR_LED 19
#define GRR_LED 18
Servo arm;

int extended_angle = 180;
int retracted_angle = 0;

String response;

void setup() {
  
  Serial.begin(9600);

  ESP32PWM::allocateTimer(0);
	ESP32PWM::allocateTimer(1);
	ESP32PWM::allocateTimer(2);
	ESP32PWM::allocateTimer(3);
  arm.setPeriodHertz(50);// Standard 50hz servo
  arm.attach(4);

  pinMode(ERR_LED,OUTPUT);
  pinMode(GRR_LED,OUTPUT);

}

void loop() {
  
  if(Serial.available() > 0)
  {
    response = Serial.readString();
  }

  if (response == "DEFECT")
  {
    digitalWrite(ERR_LED,HIGH);
    digitalWrite(GRR_LED,LOW);
    Serial.println("defected detected!!");
    arm.write(extended_angle);
    delay(1000);
    arm.write(retracted_angle);
    delay(1000);
    response = "";
  }
  
  digitalWrite(ERR_LED,LOW);
  digitalWrite(GRR_LED,HIGH);

}

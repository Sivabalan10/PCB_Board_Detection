/* Synapse 2.0 ----------REVIEW 2.0

 Added Servo functionality
 Added Buzzer functionality
 Added LCD screen functionality ( i think so )

 Need to Add Wifi ip support, thats it
  ---------------- Power over Spice is power over all ------------------
*/


#include <ESP32Servo.h> 
#include <LiquidCrystal_I2C.h>

#define ERR_LED 19 // (BUZZER LED)
#define GRR_LED 18 // (GREEN LED)

Servo arm;

LiquidCrystal_I2C lcd(0x27,20,4);

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

  // Lcd initialization
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0,0);
  lcd.print("Synapse 2.0");
  lcd.setCursor(4,1);
  lcd.print("PCB Sorter");
  delay(2000);
  lcd.clear();

}

void loop() {
  
  if(Serial.available() > 0)
  {
    response = Serial.readString();
  }

  lcd.setCursor(0,0);
  lcd.print("Nominal");

  if (response == "DEFECT")
  { 
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Defect detected!");
    digitalWrite(ERR_LED,HIGH);
    digitalWrite(GRR_LED,LOW);
    Serial.println("defected detected!!");
    arm.write(extended_angle);
    delay(1000);
    arm.write(retracted_angle);
    delay(1000);
    response = "";
    lcd.clear();
  }
  
  digitalWrite(ERR_LED,LOW);
  digitalWrite(GRR_LED,HIGH);

}

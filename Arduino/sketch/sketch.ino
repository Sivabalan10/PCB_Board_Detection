/* Synapse 2.0 ----------REVIEW 2.0

 Added Servo functionality
 Added Buzzer functionality
 Added LCD screen functionality ( i think so )

 Need to Add Wifi ip support, thats it

  ---------------- Power over Spice is power over all ------------------
*/

#include <WiFi.h>
#include <WebServer.h>
#include <ESP32Servo.h> 
#include <LiquidCrystal_I2C.h>

#define ERR_LED 19 // (BUZZER LED)
#define GRR_LED 18 // (GREEN LED)

const char* ssid = "Onichan";
const char* password = "callme@9";

WebServer server(80);

Servo arm;

LiquidCrystal_I2C lcd(0x27,20,4);


int extended_angle = 0; // intial angle womp womp 
int retracted_angle = 0;

String cause;

void setup() {
  
  Serial.begin(9600);
  
  // Wifi Connect
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

 
  server.on("/0", HTTP_GET, handleNominal); // New endpoint for normal state
  server.on("/1", HTTP_GET, handle30); // New endpoint for defect state (30)
  server.on("/2", HTTP_GET, handle60); // New endpoint for defect state (60)
  server.on("/3", HTTP_GET, handle90); // New endpoint for defect state (90)
  server.on("/4", HTTP_GET, handle120); // New endpoint for defect state (120)
  server.on("/5", HTTP_GET, handle150); // New endpoint for defect state (150)
  server.on("/6", HTTP_GET, handle180); // New endpoint for defect state (180)
  server.begin();

  Serial.println(WiFi.localIP());

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
  
  server.handleClient();

  lcd.setCursor(0,0);
  lcd.print("Nominal");
  digitalWrite(ERR_LED,LOW);
  digitalWrite(GRR_LED,HIGH);

}

void WriteAngle()
{
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print(cause);
    digitalWrite(ERR_LED,HIGH);
    digitalWrite(GRR_LED,LOW);
    Serial.println(cause);
    arm.write(extended_angle);
    delay(1000);
    arm.write(retracted_angle);
    delay(1000);
    lcd.clear();
}

void handleNominal()
{
  return;
}

void handle30()
{
  extended_angle = 30;
  WriteAngle();
  cause = "capacitor defect";
}
void handle60()
{
  extended_angle = 60;
  WriteAngle();
  cause = "resistor defect";
}
void handle90()
{
  extended_angle = 90;
  WriteAngle();
  cause = "regulator defect";
}
void handle120()
{
  extended_angle = 120;
  WriteAngle();
  cause = "switch defect";
}
void handle150()
{
  extended_angle = 150;
  WriteAngle();
  cause = "transistor defect";
}
void handle180()
{
  extended_angle = 180;
  WriteAngle();
  cause = "LED defect";
}
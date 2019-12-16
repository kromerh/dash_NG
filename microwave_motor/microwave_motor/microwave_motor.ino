#include <Servo.h>
#include <string.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int incomingInt = 0;   // for incoming serial data
String incomingStr = "0";   // for incoming serial data
String command;

void setup() {
  Serial.begin(9600);
  myservo.attach(7);  // attaches the servo on pin 9 to the servo object
}


void loop() { 
        // stop the motor
        myservo.write(90); 
        delay(200);  
        // send data only when you receive data:
        if (Serial.available() > 0) {
                // read the incoming byte:
                //incomingStr = Serial.readStringUntil('\r\n');
                String rs  = Serial.readStringUntil(','); // first value is rotation speed
                //Serial.read(); //next character is comma, so skip it using this
                String dt = Serial.readStringUntil('\r\n'); // second value is delay time
                Serial.print("Rotation speed: ");
                Serial.print(rs);
                Serial.print(" delay time: ");
                Serial.println(dt);              
                myservo.write(rs.toInt()); 
                delay(dt.toInt());  
                delay(200);              
        }
        // stop the motor
        myservo.write(90); 
        delay(200);  

  
} 

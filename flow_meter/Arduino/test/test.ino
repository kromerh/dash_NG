// ***********************************
// *** Setpoint of the mass flow
// ***********************************
int outputPinAnalog1 = 9; // Setpoint of the mass flow PIN
float V_out = 0.0;  // Setpoint of the mass flow as INTEGER from twofast-rpi3-4

void setup() {
Serial.begin(9600); // set the baud rate
Serial.println("Ready"); // print "Ready" once
}
void loop() {
  if(Serial.available() > 0) {
//    char data = Serial.read();
 //   char str[4];
  //  str[0] = data;
  //  str[1] = 'A';
  //  str[2] = 'R';
   // str[3] = 'D';

    V_out = Serial.parseFloat();
    V_out = (V_out + 0.0) * 256/5;  // 256/5 = 51
    analogWrite(outputPinAnalog1, V_out);  // Setpoing mass flow meter
    //Serial.print(str);
    Serial.print(" V_out ");
    Serial.println(V_out);
  }
}

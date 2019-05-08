int outputPinAnalog1 = 9; // Setpoint of the mass flow PIN
int V_out = 2;  // Setpoint of the mass flow as INTEGER from twofast-rpi3-4
void setup(){
   pinMode(outputPinAnalog1, OUTPUT);  // sets the pin as output
}
void loop(){
  analogWrite(outputPinAnalog1, V_out*(256/5));  // Setpoing mass flow meter
  delay(50);
}

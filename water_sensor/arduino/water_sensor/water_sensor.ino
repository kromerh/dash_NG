// ***********************************
// *** Reading of the mass flow
// ***********************************
#define S1 2  // sensor S1
#define S2 4  // sensor S2
#define S3 7  // sensor S3

void setup()
{
  Serial.begin (9600);
  pinMode(S1, INPUT);
  pinMode(S2, INPUT);
  pinMode(S3, INPUT);
}
void loop()
{
  Serial.print(digitalRead(S1));
  Serial.print(", ");
  Serial.print(digitalRead(S2));
  Serial.print(", ");
  Serial.println(digitalRead(S3));
  delay(1000);
}

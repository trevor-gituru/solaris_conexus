
void setup() {
  pinMode(A0, INPUT);
  Serial.begin(9600);
  
  // put your setup code here, to run once:

}

void loop() {
  int state = analogRead(A0);
  Serial.println(state);
  delay(1000);
  // put your main code here, to run repeatedly:

}

#include<Servo.h>
Servo servo1;
Servo servo2;
Servo servo3;
const int trig_pin = 5;
const int echo_pin = 10;
long duration;
float distance;
int ir1 = 6;
int ir2 = 9;

int ir3 = 12;
int ir4 = 8;
const int moisture_sensor_pin = A0;
const int smoke_detector = A2;
int camera_value;
void setup()
{
  // put your setup code here, to run once:
  pinMode(trig_pin,OUTPUT);
  pinMode(echo_pin,INPUT);
  Serial.begin(9600);
  pinMode(ir1,INPUT);
  pinMode(ir2,INPUT);
  servo1.attach(11);
  servo1.write(90);
  servo2.attach(3);
  servo2.write(10);
  servo3.attach(7);
  servo3.write(10);
  pinMode(smoke_detector, INPUT);

}

void loop() 
{
  Serial.println("initiation starts from here \n");
  // put your main code here, to run repeatedly:
  digitalWrite(trig_pin,LOW);
  delayMicroseconds(10);
  digitalWrite(trig_pin,HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin,LOW);
  delayMicroseconds(10);
  duration = pulseIn(echo_pin,HIGH);
  distance = duration*0.034/2;
  Serial.println("distance : ");
  Serial.println(distance);
  Serial.println("\n");
  delay(1000);
  int pin_Value_one;
  int pin_Value_two;
  pin_Value_one = digitalRead(ir1);
  Serial.println("1st IR value : ");
  Serial.println(pin_Value_one);
  delay(1000);
  pin_Value_two = digitalRead(ir2);
  Serial.println("2nd IR value :");
  Serial.println(pin_Value_two);
  delay(1000);
  int pin_Value_three = digitalRead(ir3);
  Serial.print("3rd IR value : ");
  Serial.println(pin_Value_three);
  delay(1000);
  int pin_Value_four = digitalRead(ir4);
  Serial.println("4th IR value: ");
  Serial.println(pin_Value_four);
  delay(1000);
  float moisture_percentage;
  int sensor_analog;
  sensor_analog = analogRead(moisture_sensor_pin);
  moisture_percentage = (100 - ((sensor_analog/1023.00)*100));
  Serial.println("\n");
  Serial.print(moisture_percentage);
  Serial.println("%");
  Serial.println("\n");
  int gas_sensor_read = analogRead(smoke_detector);
  Serial.println("gas_sensor_value");
  Serial.println(gas_sensor_read);
  Serial.println("\n");
  delay(1000);
  
  if(distance < 20)
  {
    if(pin_Value_one == 0 || pin_Value_two == 0 || pin_Value_three == 0 || pin_Value_four == 0)
    {
      servo1.write(180);
      Serial.print("ok");
      delay(1000);
      servo1.write(0);
      delay(1000);
      servo1.write(90);
      delay(1000);
      if (Serial.available() > 0) 
        {
          char received = Serial.read();
    
         if (received == '1')
         {
          Serial.print("Recyclabe\n");
          delay(1000);
          servo2.write(90);
          delay(1000);
         } 
       else if (received == '0') 
       {
          Serial.println("Received: Non-Recyclable (0)");
          if(gas_sensor_read < 90)
          {
            Serial.println(gas_sensor_read);
            if(moisture_percentage < 150)
            {
              Serial.println("Recyclable");
              delay(1000);
              servo2.write(90);
              delay(1000);
              servo2.write(0);
            }
            else
            {
              Serial.println("non recyclable");
              delay(1000);
              servo3.write(90);
              delay(1000);
              servo3.write(0);
              delay(1000);
            }
          }
          else
         {
          servo3.write(90);
              delay(1000);
              servo3.write(0);
              delay(1000);
          }
        }
    } 
    else 
    {
      Serial.println("Received unknown data");
      if(gas_sensor_read < 90)
          {
            Serial.println(gas_sensor_read);
            if(moisture_percentage < 150)
            {
              Serial.println("Recyclable");
              delay(1000);
              servo2.write(90);
              delay(1000);
              servo2.write(0);
              delay(1000);
            }
            else
            {
              Serial.println("non recyclable");
              delay(1000);
              servo3.write(90);
              delay(1000);
              servo3.write(0);
            }
          }
          else
         {
          servo3.write(90);
              delay(1000);
              servo3.write(0);
              delay(1000);
          }
        
    }
  
  }
}
}

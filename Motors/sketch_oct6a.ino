// Motor 1
const int PWM1 = 6;
const int DIR1 = 7;

// Motor 2
const int PWM2 = 5;
const int DIR2 = 4;

// Motor 3
const int PWM3 = 9;
const int DIR3 = 8;

// Motor 4
const int PWM4 = 10;
const int DIR4 = 12;

void setup()
{
  pinMode(PWM1, OUTPUT);
  pinMode(DIR1, OUTPUT);

  pinMode(PWM2, OUTPUT);
  pinMode(DIR2, OUTPUT);

  pinMode(PWM3, OUTPUT);
  pinMode(DIR3, OUTPUT);

  pinMode(PWM4, OUTPUT);
  pinMode(DIR4, OUTPUT);

  // Start all motors stopped
  stopRover();
}

void loop()
{
  // Forward
  forward(120);
  delay(2000);

  // Stop
  stopRover();
  delay(1000);

  // Backward
  backward(120);
  delay(2000);

  // Stop
  stopRover();
  delay(2000);
}


void forward(int speed)
{
  digitalWrite(DIR1, HIGH);
  digitalWrite(DIR2, HIGH);
  digitalWrite(DIR3, HIGH);
  digitalWrite(DIR4, HIGH);

  analogWrite(PWM1, speed);
  analogWrite(PWM2, speed);
  analogWrite(PWM3, speed);
  analogWrite(PWM4, speed);
}


void backward(int speed)
{
  digitalWrite(DIR1, LOW);
  digitalWrite(DIR2, LOW);
  digitalWrite(DIR3, LOW);
  digitalWrite(DIR4, LOW);

  analogWrite(PWM1, speed);
  analogWrite(PWM2, speed);
  analogWrite(PWM3, speed);
  analogWrite(PWM4, speed);
}


void stopRover()
{
  analogWrite(PWM1, 0);
  analogWrite(PWM2, 0);
  analogWrite(PWM3, 0);
  analogWrite(PWM4, 0);
}
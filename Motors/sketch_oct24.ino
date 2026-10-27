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

const int MOTOR_SPEED = 120;

void setup()
{
  Serial.begin(115200);

  pinMode(PWM1, OUTPUT);
  pinMode(DIR1, OUTPUT);

  pinMode(PWM2, OUTPUT);
  pinMode(DIR2, OUTPUT);

  pinMode(PWM3, OUTPUT);
  pinMode(DIR3, OUTPUT);

  pinMode(PWM4, OUTPUT);
  pinMode(DIR4, OUTPUT);

  stopRover();
}

void loop()
{
  if (Serial.available() > 0)
  {
    char command = Serial.read();

    switch (command)
    {
      case 'F':
        forward(MOTOR_SPEED);
        break;

      case 'B':
        backward(MOTOR_SPEED);
        break;

      case 'L':
        turnLeft(MOTOR_SPEED);
        break;

      case 'R':
        turnRight(MOTOR_SPEED);
        break;

      case 'S':
        stopRover();
        break;
    }
  }
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

void turnLeft(int speed)
{
  // Stop LEFT side - Motors 3 and 4
  analogWrite(PWM3, 0);
  analogWrite(PWM4, 0);

  // Drive RIGHT side forward - Motors 1 and 2
  digitalWrite(DIR1, HIGH);
  digitalWrite(DIR2, HIGH);

  analogWrite(PWM1, speed);
  analogWrite(PWM2, speed);
}


void turnRight(int speed)
{
  // Stop RIGHT side - Motors 1 and 2
  analogWrite(PWM1, 0);
  analogWrite(PWM2, 0);

  // Drive LEFT side forward - Motors 3 and 4
  digitalWrite(DIR3, HIGH);
  digitalWrite(DIR4, HIGH);

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
// ==============================
// Rover Motor Pin Configuration
// ==============================

// RIGHT SIDE
const int PWM1 = 6;
const int DIR1 = 7;

const int PWM2 = 5;
const int DIR2 = 4;

// LEFT SIDE
const int PWM3 = 9;
const int DIR3 = 8;

const int PWM4 = 10;
const int DIR4 = 12;


// Safety timeout
unsigned long lastCommandTime = 0;
const unsigned long COMMAND_TIMEOUT = 500;  // milliseconds


void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(20);

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
  // Expected format from Raspberry Pi:
  //
  // LEFT_SPEED,RIGHT_SPEED
  //
  // Example:
  // 150,150
  // -150,-150
  // 150,-150

  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');
    command.trim();

    int commaIndex = command.indexOf(',');

    if (commaIndex > 0)
    {
      int leftSpeed =
        command.substring(0, commaIndex).toInt();

      int rightSpeed =
        command.substring(commaIndex + 1).toInt();

      // Keep PWM values within valid range
      leftSpeed = constrain(leftSpeed, -255, 255);
      rightSpeed = constrain(rightSpeed, -255, 255);

      setDrive(leftSpeed, rightSpeed);

      lastCommandTime = millis();
    }
  }


  // SAFETY:
  // Stop motors if communication with Pi is lost
  if (millis() - lastCommandTime > COMMAND_TIMEOUT)
  {
    stopRover();
  }
}


// ==============================
// Drive Control
// ==============================

void setDrive(int leftSpeed, int rightSpeed)
{
  // LEFT SIDE - Motors 3 and 4
  setMotor(PWM3, DIR3, leftSpeed);
  setMotor(PWM4, DIR4, leftSpeed);

  // RIGHT SIDE - Motors 1 and 2
  setMotor(PWM1, DIR1, rightSpeed);
  setMotor(PWM2, DIR2, rightSpeed);
}


// ==============================
// Individual Motor Control
// ==============================

void setMotor(int pwmPin, int dirPin, int speed)
{
  if (speed > 0)
  {
    // Forward
    digitalWrite(dirPin, HIGH);
    analogWrite(pwmPin, speed);
  }

  else if (speed < 0)
  {
    // Backward
    digitalWrite(dirPin, LOW);
    analogWrite(pwmPin, abs(speed));
  }

  else
  {
    // Stop
    analogWrite(pwmPin, 0);
  }
}


// ==============================
// Emergency / Normal Stop
// ==============================

void stopRover()
{
  analogWrite(PWM1, 0);
  analogWrite(PWM2, 0);
  analogWrite(PWM3, 0);
  analogWrite(PWM4, 0);
}
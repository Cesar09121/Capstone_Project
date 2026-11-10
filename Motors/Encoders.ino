#include <avr/interrupt.h>

// =====================================
// MOTOR PIN CONFIGURATION
// =====================================

// RIGHT SIDE

// Motor 1 - Front Right
const int PWM1 = 6;
const int DIR1 = 7;

// Motor 2 - Rear Right
const int PWM2 = 5;
const int DIR2 = 4;


// LEFT SIDE

// Motor 3 - Front Left
const int PWM3 = 9;
const int DIR3 = 8;

// Motor 4 - Rear Left
const int PWM4 = 10;
const int DIR4 = 12;


// =====================================
// ENCODER PIN CONFIGURATION
// =====================================

// Green C1 wires

const int ENC1 = 2;    // Front Right
const int ENC2 = 3;    // Rear Right
const int ENC3 = 11;   // Front Left
const int ENC4 = 13;   // Rear Left


// =====================================
// ENCODER COUNTERS
// =====================================

volatile unsigned long encoderCount1 = 0;
volatile unsigned long encoderCount2 = 0;
volatile unsigned long encoderCount3 = 0;
volatile unsigned long encoderCount4 = 0;


// Used for detecting rising edges on pins 11 and 13
volatile uint8_t previousPortB;


// =====================================
// ENCODER / WHEEL CONSTANTS
// =====================================

// Encoder produces 11 pulses per motor revolution
const float ENCODER_PPR = 11.0;

// 110 RPM motor gearbox
const float GEAR_RATIO = 90.0;

// Pulses for one wheel/output shaft revolution
const float PULSES_PER_REV =
    ENCODER_PPR * GEAR_RATIO;

// Wheel diameter = 65 mm
const float WHEEL_DIAMETER_M = 0.065;

// Wheel circumference
const float WHEEL_CIRCUMFERENCE_M =
    PI * WHEEL_DIAMETER_M;


// =====================================
// TIMING
// =====================================

// Calculate RPM twice per second
const unsigned long TELEMETRY_INTERVAL = 500;

unsigned long lastTelemetryTime = 0;


// Stop rover if commands from Pi stop arriving
const unsigned long COMMAND_TIMEOUT = 500;

unsigned long lastCommandTime = 0;


// =====================================
// SETUP
// =====================================

void setup()
{
  Serial.begin(115200);
  Serial.setTimeout(20);


  // -------------------------
  // Motor Pins
  // -------------------------

  pinMode(PWM1, OUTPUT);
  pinMode(DIR1, OUTPUT);

  pinMode(PWM2, OUTPUT);
  pinMode(DIR2, OUTPUT);

  pinMode(PWM3, OUTPUT);
  pinMode(DIR3, OUTPUT);

  pinMode(PWM4, OUTPUT);
  pinMode(DIR4, OUTPUT);


  // -------------------------
  // Encoder Pins
  // -------------------------

  pinMode(ENC1, INPUT_PULLUP);
  pinMode(ENC2, INPUT_PULLUP);
  pinMode(ENC3, INPUT_PULLUP);
  pinMode(ENC4, INPUT_PULLUP);


  // Pins 2 and 3 support normal external interrupts
  attachInterrupt(
      digitalPinToInterrupt(ENC1),
      encoder1ISR,
      RISING
  );

  attachInterrupt(
      digitalPinToInterrupt(ENC2),
      encoder2ISR,
      RISING
  );


  // -------------------------
  // Pin Change Interrupts
  // for Pins 11 and 13
  // -------------------------

  previousPortB = PINB;

  // Enable pin-change interrupts for Port B
  PCICR |= (1 << PCIE0);

  // Pin 11 = PB3 = PCINT3
  PCMSK0 |= (1 << PCINT3);

  // Pin 13 = PB5 = PCINT5
  PCMSK0 |= (1 << PCINT5);


  stopRover();

  lastTelemetryTime = millis();

  Serial.println("Rover controller started");
  Serial.println("Encoder telemetry active");
}


// =====================================
// MAIN LOOP
// =====================================

void loop()
{
  // ---------------------------------
  // Receive motor commands from Pi
  // ---------------------------------

  if (Serial.available() > 0)
  {
    String command = Serial.readStringUntil('\n');

    command.trim();

    int commaIndex = command.indexOf(',');

    if (commaIndex > 0)
    {
      int leftSpeed =
          command.substring(
              0,
              commaIndex
          ).toInt();

      int rightSpeed =
          command.substring(
              commaIndex + 1
          ).toInt();


      leftSpeed =
          constrain(leftSpeed, -255, 255);

      rightSpeed =
          constrain(rightSpeed, -255, 255);


      setDrive(
          leftSpeed,
          rightSpeed
      );

      lastCommandTime = millis();
    }
  }


  // ---------------------------------
  // Safety Timeout
  // ---------------------------------

  if (millis() - lastCommandTime >
      COMMAND_TIMEOUT)
  {
    stopRover();
  }


  // ---------------------------------
  // Calculate Encoder Telemetry
  // ---------------------------------

  unsigned long currentTime = millis();

  if (currentTime - lastTelemetryTime >=
      TELEMETRY_INTERVAL)
  {
    calculateTelemetry(currentTime);
  }
}


// =====================================
// MOTOR CONTROL
// =====================================

void setDrive(
    int leftSpeed,
    int rightSpeed
)
{
  // LEFT SIDE
  // Motors 3 and 4

  setMotor(
      PWM3,
      DIR3,
      leftSpeed
  );

  setMotor(
      PWM4,
      DIR4,
      leftSpeed
  );


  // RIGHT SIDE
  // Motors 1 and 2

  setMotor(
      PWM1,
      DIR1,
      rightSpeed
  );

  setMotor(
      PWM2,
      DIR2,
      rightSpeed
  );
}


// =====================================
// INDIVIDUAL MOTOR CONTROL
// =====================================

void setMotor(
    int pwmPin,
    int dirPin,
    int speed
)
{
  if (speed > 0)
  {
    digitalWrite(
        dirPin,
        HIGH
    );

    analogWrite(
        pwmPin,
        speed
    );
  }

  else if (speed < 0)
  {
    digitalWrite(
        dirPin,
        LOW
    );

    analogWrite(
        pwmPin,
        abs(speed)
    );
  }

  else
  {
    analogWrite(
        pwmPin,
        0
    );
  }
}


// =====================================
// STOP ALL MOTORS
// =====================================

void stopRover()
{
  analogWrite(PWM1, 0);
  analogWrite(PWM2, 0);
  analogWrite(PWM3, 0);
  analogWrite(PWM4, 0);
}


// =====================================
// ENCODER INTERRUPTS
// =====================================

// Motor 1 - Front Right
void encoder1ISR()
{
  encoderCount1++;
}


// Motor 2 - Rear Right
void encoder2ISR()
{
  encoderCount2++;
}


// =====================================
// PIN CHANGE INTERRUPT
// Pins 11 and 13
// =====================================

ISR(PCINT0_vect)
{
  uint8_t currentPortB = PINB;

  uint8_t changed =
      currentPortB ^ previousPortB;


  // --------------------------------
  // Motor 3
  // Pin 11 = PB3
  // Count rising edge
  // --------------------------------

  if (
      (changed & (1 << PB3)) &&
      (currentPortB & (1 << PB3))
     )
  {
    encoderCount3++;
  }


  // --------------------------------
  // Motor 4
  // Pin 13 = PB5
  // Count rising edge
  // --------------------------------

  if (
      (changed & (1 << PB5)) &&
      (currentPortB & (1 << PB5))
     )
  {
    encoderCount4++;
  }


  previousPortB = currentPortB;
}


// =====================================
// RPM + SPEED CALCULATION
// =====================================

void calculateTelemetry(
    unsigned long currentTime
)
{
  unsigned long elapsedTime =
      currentTime - lastTelemetryTime;


  // Temporarily disable interrupts
  // while copying pulse counts

  noInterrupts();

  unsigned long count1 =
      encoderCount1;

  unsigned long count2 =
      encoderCount2;

  unsigned long count3 =
      encoderCount3;

  unsigned long count4 =
      encoderCount4;


  // Reset counters for next interval

  encoderCount1 = 0;
  encoderCount2 = 0;
  encoderCount3 = 0;
  encoderCount4 = 0;

  interrupts();


  // ---------------------------------
  // RPM Calculation
  // ---------------------------------

  float rpm1 =
      (count1 * 60000.0) /
      (PULSES_PER_REV * elapsedTime);

  float rpm2 =
      (count2 * 60000.0) /
      (PULSES_PER_REV * elapsedTime);

  float rpm3 =
      (count3 * 60000.0) /
      (PULSES_PER_REV * elapsedTime);

  float rpm4 =
      (count4 * 60000.0) /
      (PULSES_PER_REV * elapsedTime);


  // ---------------------------------
  // Linear Speed - meters/second
  // ---------------------------------

  float speed1 =
      (rpm1 * WHEEL_CIRCUMFERENCE_M)
      / 60.0;

  float speed2 =
      (rpm2 * WHEEL_CIRCUMFERENCE_M)
      / 60.0;

  float speed3 =
      (rpm3 * WHEEL_CIRCUMFERENCE_M)
      / 60.0;

  float speed4 =
      (rpm4 * WHEEL_CIRCUMFERENCE_M)
      / 60.0;


  // ---------------------------------
  // Convert m/s to MPH
  // ---------------------------------

  float mph1 =
      speed1 * 2.23694;

  float mph2 =
      speed2 * 2.23694;

  float mph3 =
      speed3 * 2.23694;

  float mph4 =
      speed4 * 2.23694;


  // =================================
  // SEND TELEMETRY
  //
  // Order:
  // Front Left
  // Front Right
  // Rear Left
  // Rear Right
  // =================================

  Serial.print("TEL,");

  // Front Left - Motor 3
  Serial.print(rpm3, 1);
  Serial.print(",");

  // Front Right - Motor 1
  Serial.print(rpm1, 1);
  Serial.print(",");

  // Rear Left - Motor 4
  Serial.print(rpm4, 1);
  Serial.print(",");

  // Rear Right - Motor 2
  Serial.print(rpm2, 1);

  Serial.print(",");


  // Speeds in MPH

  // Front Left
  Serial.print(mph3, 2);
  Serial.print(",");

  // Front Right
  Serial.print(mph1, 2);
  Serial.print(",");

  // Rear Left
  Serial.print(mph4, 2);
  Serial.print(",");

  // Rear Right
  Serial.println(mph2, 2);


  lastTelemetryTime =
      currentTime;
}
import os
import time
import serial

# Prevent pygame from needing a graphical window
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame


# =====================================
# Arduino Serial Connection
# =====================================

arduino = serial.Serial(
    "/dev/ttyACM0",
    115200,
    timeout=0
)

# Arduino resets when serial connection opens
time.sleep(2)

# Clear any startup messages already waiting
arduino.reset_input_buffer()


# =====================================
# PS5 Controller Setup
# =====================================

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected.")
    arduino.close()
    pygame.quit()
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()

print("Controller connected:")
print(controller.get_name())

print()
print("Left stick controls rover.")
print("Encoder telemetry active.")
print("Press Ctrl+C to quit.")
print()


# =====================================
# Controller Settings
# =====================================

DEADZONE = 0.10
MAX_SPEED = 255


def apply_deadzone(value):
    if abs(value) < DEADZONE:
        return 0.0

    return value


# =====================================
# Send Drive Command
# =====================================

def send_drive(left_speed, right_speed):

    command = f"{left_speed},{right_speed}\n"

    arduino.write(command.encode())


# =====================================
# Read Arduino Telemetry
# =====================================

def read_telemetry():

    while arduino.in_waiting > 0:

        line = arduino.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()

        if not line.startswith("TEL,"):
            continue

        parts = line.split(",")

        # Expected:
        # TEL,
        # FL RPM,
        # FR RPM,
        # RL RPM,
        # RR RPM,
        # FL MPH,
        # FR MPH,
        # RL MPH,
        # RR MPH

        if len(parts) != 9:
            continue

        try:

            front_left_rpm = float(parts[1])
            front_right_rpm = float(parts[2])
            rear_left_rpm = float(parts[3])
            rear_right_rpm = float(parts[4])

            front_left_mph = float(parts[5])
            front_right_mph = float(parts[6])
            rear_left_mph = float(parts[7])
            rear_right_mph = float(parts[8])

            print(
                "\n"
                f"Front Left : {front_left_rpm:6.1f} RPM | "
                f"{front_left_mph:.2f} MPH\n"
                f"Front Right: {front_right_rpm:6.1f} RPM | "
                f"{front_right_mph:.2f} MPH\n"
                f"Rear Left  : {rear_left_rpm:6.1f} RPM | "
                f"{rear_left_mph:.2f} MPH\n"
                f"Rear Right : {rear_right_rpm:6.1f} RPM | "
                f"{rear_right_mph:.2f} MPH"
            )

        except ValueError:
            pass


# =====================================
# Main Program
# =====================================

try:

    while True:

        pygame.event.pump()

        # PS5 left analog stick
        steering = controller.get_axis(0)
        throttle = -controller.get_axis(1)

        steering = apply_deadzone(steering)
        throttle = apply_deadzone(throttle)


        # ---------------------------------
        # Differential / Arcade Drive Mixing
        # ---------------------------------

        left = throttle + steering
        right = throttle - steering


        # Prevent values from exceeding +/-1
        largest = max(
            1.0,
            abs(left),
            abs(right)
        )

        left /= largest
        right /= largest


        # Convert to Arduino PWM range
        left_speed = int(left * MAX_SPEED)
        right_speed = int(right * MAX_SPEED)


        # Send motor command
        send_drive(
            left_speed,
            right_speed
        )


        # Read encoder RPM / speed
        read_telemetry()


        # 20 updates per second
        time.sleep(0.05)


except KeyboardInterrupt:

    print("\nStopping rover...")

    send_drive(0, 0)


finally:

    arduino.close()
    pygame.quit()
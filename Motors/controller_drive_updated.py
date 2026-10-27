import os
import time
import serial

# Prevent pygame from needing a graphical window
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame


# --------------------------------
# Arduino Serial Connection
# --------------------------------

arduino = serial.Serial(
    "/dev/ttyACM0",
    115200,
    timeout=1
)

# Arduino usually resets when serial opens
time.sleep(2)


# --------------------------------
# PS5 Controller Setup
# --------------------------------

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
print("Push forward/backward to drive.")
print("Push left/right for zero-turn steering.")
print("Press Ctrl+C to quit.")


# --------------------------------
# Settings
# --------------------------------

DEADZONE = 0.10
MAX_SPEED = 255


def apply_deadzone(value):
    if abs(value) < DEADZONE:
        return 0.0

    return value


def send_drive(left_speed, right_speed):
    command = f"{left_speed},{right_speed}\n"

    arduino.write(command.encode())

    print(
        f"Left: {left_speed:4d} | "
        f"Right: {right_speed:4d}"
    )


# --------------------------------
# Main Control Loop
# --------------------------------

try:
    while True:

        pygame.event.pump()

        # DualSense left stick
        steering = controller.get_axis(0)
        throttle = -controller.get_axis(1)

        steering = apply_deadzone(steering)
        throttle = apply_deadzone(throttle)

        # Arcade / differential drive mixing
        left = throttle + steering
        right = throttle - steering

        # Normalize so neither side exceeds 1.0
        largest = max(
            1.0,
            abs(left),
            abs(right)
        )

        left /= largest
        right /= largest

        # Convert from -1.0...1.0 to -255...255
        left_speed = int(left * MAX_SPEED)
        right_speed = int(right * MAX_SPEED)

        send_drive(left_speed, right_speed)

        # Send frequently enough to satisfy Arduino safety timeout
        time.sleep(0.05)


except KeyboardInterrupt:

    print("\nStopping rover...")

    send_drive(0, 0)


finally:

    arduino.close()
    pygame.quit()
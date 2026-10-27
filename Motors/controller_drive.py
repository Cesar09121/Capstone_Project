import os
import time
import serial

# Prevent pygame from needing a graphical window
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame


# -------------------------
# Arduino Serial Connection
# -------------------------

arduino = serial.Serial(
    "/dev/ttyACM0",
    115200,
    timeout=1
)

# Arduino resets when serial connection opens
time.sleep(2)


# -------------------------
# PS5 Controller Setup
# -------------------------

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected.")
    arduino.close()
    exit()

controller = pygame.joystick.Joystick(0)
controller.init()

print("Controller connected:")
print(controller.get_name())

print()
print("Left stick controls rover")
print("Press Ctrl+C to quit")


# -------------------------
# Driving Settings
# -------------------------

DEADZONE = 0.35

last_command = None


def send_command(command):
    global last_command

    # Only send when direction changes
    if command != last_command:
        arduino.write(command.encode())
        print("Command:", command)
        last_command = command


# -------------------------
# Main Control Loop
# -------------------------

try:

    while True:

        pygame.event.pump()

        # DualSense left stick
        left_x = controller.get_axis(0)
        left_y = controller.get_axis(1)

        # Determine which direction the stick is pushed most
        if abs(left_y) > abs(left_x):

            if left_y < -DEADZONE:
                send_command("F")

            elif left_y > DEADZONE:
                send_command("B")

            else:
                send_command("S")

        else:

            if left_x < -DEADZONE:
                send_command("L")

            elif left_x > DEADZONE:
                send_command("R")

            else:
                send_command("S")

        time.sleep(0.05)


except KeyboardInterrupt:

    print("\nStopping rover...")
    arduino.write(b"S")


finally:

    arduino.close()
    pygame.quit()
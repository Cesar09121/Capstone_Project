import json
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
# Telemetry File (shared with server.py)
# =====================================

# /dev/shm is stored in RAM, so frequent writes don't wear out the SD card
TELEMETRY_FILE = "/dev/shm/rover_telemetry.json"

# Save telemetry 4 times per second
SAVE_INTERVAL = 0.25

# Latest encoder values from the Arduino
telemetry = {
    "rpm": {"FL": 0, "FR": 0, "RL": 0, "RR": 0},
    "mph": {"FL": 0, "FR": 0, "RL": 0, "RR": 0},
}

# Holds partial serial lines until the rest arrives
serial_buffer = ""


# =====================================
# PS5 Controller Setup
# =====================================

pygame.init()
pygame.joystick.init()

controller = None

if pygame.joystick.get_count() > 0:
    controller = pygame.joystick.Joystick(0)
    controller.init()

    print("Controller connected:")
    print(controller.get_name())
else:
    print("No controller detected. Waiting for controller...")

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
# Controller Connect / Disconnect
# =====================================

def check_controller_events():
    global controller

    for event in pygame.event.get():

        # Controller turned off or out of range
        if event.type == pygame.JOYDEVICEREMOVED:
            controller = None
            send_drive(0, 0)
            print("Controller disconnected. Rover stopped.")

        # Controller turned on or reconnected
        elif event.type == pygame.JOYDEVICEADDED and controller is None:
            controller = pygame.joystick.Joystick(event.device_index)
            controller.init()
            print("Controller connected:", controller.get_name())


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
    global serial_buffer

    # Add everything waiting on the serial port to the buffer
    waiting = arduino.in_waiting

    if waiting > 0:
        serial_buffer += arduino.read(waiting).decode(
            "utf-8",
            errors="ignore"
        )

    # Only handle complete lines, keep the unfinished part for later
    while "\n" in serial_buffer:

        line, serial_buffer = serial_buffer.split("\n", 1)
        line = line.strip()

        if not line.startswith("TEL,"):
            continue

        parts = line.split(",")

        # Expected:
        # TEL,
        # FL RPM, FR RPM, RL RPM, RR RPM,
        # FL MPH, FR MPH, RL MPH, RR MPH

        if len(parts) != 9:
            continue

        try:
            values = [float(part) for part in parts[1:]]
        except ValueError:
            continue

        telemetry["rpm"] = {
            "FL": values[0],
            "FR": values[1],
            "RL": values[2],
            "RR": values[3],
        }

        telemetry["mph"] = {
            "FL": values[4],
            "FR": values[5],
            "RL": values[6],
            "RR": values[7],
        }


# =====================================
# Save Telemetry for the Dashboard
# =====================================

def save_telemetry():
    data = {
        "time": time.time(),
        "controllerConnected": controller is not None,
        "rpm": telemetry["rpm"],
        "mph": telemetry["mph"],
    }

    # Write to a temporary file first, then swap it in,
    # so server.py never reads a half-written file
    temp_file = TELEMETRY_FILE + ".tmp"

    with open(temp_file, "w") as file:
        json.dump(data, file)

    os.replace(temp_file, TELEMETRY_FILE)


# =====================================
# Main Program
# =====================================

last_save = 0

try:

    while True:

        check_controller_events()

        # No controller: keep the rover stopped
        if controller is None:
            send_drive(0, 0)

        else:
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


        # Share telemetry with server.py
        if time.time() - last_save >= SAVE_INTERVAL:
            save_telemetry()
            last_save = time.time()


        # 20 updates per second
        time.sleep(0.05)


except KeyboardInterrupt:

    print("\nStopping rover...")

    send_drive(0, 0)


finally:

    arduino.close()
    pygame.quit()
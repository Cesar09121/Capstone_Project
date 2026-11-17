import pygame
import serial
import time

ARM_PORT = "/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0"
BAUD_RATE = 9600

DEADZONE = 0.20

# -----------------------------
# ID6 - Base Rotation
# -----------------------------
BASE_MIN = 1200
BASE_MAX = 1800
BASE_STEP = 5
base_position = 1500

# -----------------------------
# ID5 - Shoulder
# -----------------------------
SHOULDER_MIN = 1200
SHOULDER_MAX = 1800
SHOULDER_STEP = 5
shoulder_position = 1500

# -----------------------------
# ID4 - Elbow
# -----------------------------
ELBOW_MIN = 900
ELBOW_MAX = 1800
ELBOW_STEP = 5
elbow_position = 1500

# -----------------------------
# ID3 - Wrist Pitch
# -----------------------------
WRIST_PITCH_MIN = 1200
WRIST_PITCH_MAX = 1800
WRIST_PITCH_STEP = 5
wrist_pitch_position = 1500

# -----------------------------
# ID2 - Wrist Rotation
# -----------------------------
WRIST_ROTATE_MIN = 1200
WRIST_ROTATE_MAX = 1800
WRIST_ROTATE_STEP = 5
wrist_rotate_position = 1500

# -----------------------------
# ID1 - Gripper
# -----------------------------
GRIPPER_MIN = 1200
GRIPPER_MAX = 1500
GRIPPER_STEP = 5
gripper_position = 1500

# -----------------------------
# DualSense Button Mapping
# -----------------------------
CROSS_BUTTON = 0
CIRCLE_BUTTON = 1
TRIANGLE_BUTTON = 2
SQUARE_BUTTON = 3

L1_BUTTON = 4
R1_BUTTON = 5

L2_BUTTON = 6
R2_BUTTON = 7


def move_servo(ser, servo_id, pulse, duration=80):
    pulse = int(pulse)

    # General PWM safety range
    pulse = max(500, min(2500, pulse))

    # Gripper safety limit
    if servo_id == 1:
        pulse = min(pulse, 1500)

    time_low = duration & 0xFF
    time_high = (duration >> 8) & 0xFF

    pulse_low = pulse & 0xFF
    pulse_high = (pulse >> 8) & 0xFF

    packet = bytes([
        0x55,
        0x55,
        0x08,
        0x03,
        0x01,
        time_low,
        time_high,
        servo_id,
        pulse_low,
        pulse_high
    ])

    ser.write(packet)


# -----------------------------
# Initialize PS5 Controller
# -----------------------------
pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("No controller detected.")
    raise SystemExit

controller = pygame.joystick.Joystick(0)
controller.init()


# -----------------------------
# Connect to LeArm ESP32
# -----------------------------
arm = serial.Serial(
    ARM_PORT,
    BAUD_RATE,
    timeout=0.5
)

time.sleep(2)

print(f"Controller: {controller.get_name()}")
print("Arm connected.")
print()
print("RIGHT STICK X = Base rotation")
print("RIGHT STICK Y = Shoulder up/down")
print("L1 / R1 = Elbow")
print("SQUARE / X = Wrist pitch")
print("CIRCLE / TRIANGLE = Wrist rotation")
print("L2 / R2 = Gripper")
print("LEFT STICK = Rover only / untouched")
print("Ctrl+C to stop")
print()


try:
    while True:

        pygame.event.pump()

        # -----------------------------
        # Controller Inputs
        # -----------------------------
        right_x = controller.get_axis(3)
        right_y = controller.get_axis(4)

        l1_pressed = controller.get_button(L1_BUTTON)
        r1_pressed = controller.get_button(R1_BUTTON)

        square_pressed = controller.get_button(SQUARE_BUTTON)
        cross_pressed = controller.get_button(CROSS_BUTTON)

        circle_pressed = controller.get_button(CIRCLE_BUTTON)
        triangle_pressed = controller.get_button(TRIANGLE_BUTTON)

        l2_pressed = controller.get_button(L2_BUTTON)
        r2_pressed = controller.get_button(R2_BUTTON)

        # Save previous positions
        old_base = base_position
        old_shoulder = shoulder_position
        old_elbow = elbow_position
        old_wrist_pitch = wrist_pitch_position
        old_wrist_rotate = wrist_rotate_position
        old_gripper = gripper_position

        # -----------------------------
        # ID6 - Base Rotation
        # -----------------------------
        if right_x > DEADZONE:
            base_position += BASE_STEP

        elif right_x < -DEADZONE:
            base_position -= BASE_STEP

        base_position = max(
            BASE_MIN,
            min(BASE_MAX, base_position)
        )

        # -----------------------------
        # ID5 - Shoulder
        # -----------------------------
        # Stick UP = shoulder UP
        if right_y < -DEADZONE:
            shoulder_position += SHOULDER_STEP

        # Stick DOWN = shoulder DOWN
        elif right_y > DEADZONE:
            shoulder_position -= SHOULDER_STEP

        shoulder_position = max(
            SHOULDER_MIN,
            min(SHOULDER_MAX, shoulder_position)
        )

        # -----------------------------
        # ID4 - Elbow
        # -----------------------------
        if l1_pressed:
            elbow_position -= ELBOW_STEP

        elif r1_pressed:
            elbow_position += ELBOW_STEP

        elbow_position = max(
            ELBOW_MIN,
            min(ELBOW_MAX, elbow_position)
        )

        # -----------------------------
        # ID3 - Wrist Pitch
        # -----------------------------
        # Square = one direction
        if square_pressed:
            wrist_pitch_position += WRIST_PITCH_STEP

        # X = opposite direction
        elif cross_pressed:
            wrist_pitch_position -= WRIST_PITCH_STEP

        wrist_pitch_position = max(
            WRIST_PITCH_MIN,
            min(WRIST_PITCH_MAX, wrist_pitch_position)
        )

        # -----------------------------
        # ID2 - Wrist Rotation
        # -----------------------------
        # Circle = one direction
        if circle_pressed:
            wrist_rotate_position -= WRIST_ROTATE_STEP

        # Triangle = opposite direction
        elif triangle_pressed:
            wrist_rotate_position += WRIST_ROTATE_STEP

        wrist_rotate_position = max(
            WRIST_ROTATE_MIN,
            min(WRIST_ROTATE_MAX, wrist_rotate_position)
        )

        # -----------------------------
        # ID1 - Gripper
        # -----------------------------
        # L2 = Open
        if l2_pressed:
            gripper_position -= GRIPPER_STEP

        # R2 = Close
        elif r2_pressed:
            gripper_position += GRIPPER_STEP

        gripper_position = max(
            GRIPPER_MIN,
            min(GRIPPER_MAX, gripper_position)
        )

        # -----------------------------
        # Send Servo Commands
        # -----------------------------
        if base_position != old_base:
            move_servo(
                arm,
                6,
                base_position,
                80
            )

        if shoulder_position != old_shoulder:
            move_servo(
                arm,
                5,
                shoulder_position,
                80
            )

        if elbow_position != old_elbow:
            move_servo(
                arm,
                4,
                elbow_position,
                80
            )

        if wrist_pitch_position != old_wrist_pitch:
            move_servo(
                arm,
                3,
                wrist_pitch_position,
                80
            )

        if wrist_rotate_position != old_wrist_rotate:
            move_servo(
                arm,
                2,
                wrist_rotate_position,
                80
            )

        if gripper_position != old_gripper:
            move_servo(
                arm,
                1,
                gripper_position,
                80
            )

        # -----------------------------
        # Console Output
        # -----------------------------
        if (
            base_position != old_base
            or shoulder_position != old_shoulder
            or elbow_position != old_elbow
            or wrist_pitch_position != old_wrist_pitch
            or wrist_rotate_position != old_wrist_rotate
            or gripper_position != old_gripper
        ):

            print(
                f"Gripper: {gripper_position} | "
                f"Wrist Rotate: {wrist_rotate_position} | "
                f"Wrist Pitch: {wrist_pitch_position} | "
                f"Elbow: {elbow_position} | "
                f"Shoulder: {shoulder_position} | "
                f"Base: {base_position}",
                end="\r"
            )

        time.sleep(0.03)


except KeyboardInterrupt:
    print("\nStopping arm controller...")


finally:
    arm.close()
    pygame.quit()
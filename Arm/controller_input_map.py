import pygame
import time

pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()

print(f"Controller: {controller.get_name()}")
print("Press buttons / move controls.")
print("Ctrl+C to stop.\n")

try:
    while True:
        for event in pygame.event.get():

            if event.type == pygame.JOYBUTTONDOWN:
                print(f"BUTTON {event.button} PRESSED")

            elif event.type == pygame.JOYBUTTONUP:
                print(f"BUTTON {event.button} RELEASED")

            elif event.type == pygame.JOYAXISMOTION:
                if abs(event.value) > 0.5:
                    print(
                        f"AXIS {event.axis}: "
                        f"{event.value:.2f}"
                    )

            elif event.type == pygame.JOYHATMOTION:
                print(f"D-PAD: {event.value}")

        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped.")

finally:
    pygame.quit()
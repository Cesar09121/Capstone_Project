import time

import cv2
import numpy as np
import board
import busio
import adafruit_mlx90640


# Start I2C
i2c = busio.I2C(board.SCL, board.SDA, frequency=800000)

# Start MLX90640
mlx = adafruit_mlx90640.MLX90640(i2c)

# Refresh rate
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_4_HZ

# 32 x 24 = 768 temperature values
frame = [0] * 768

print("Thermal camera started")
print("Press Q to quit")


while True:
    try:
        mlx.getFrame(frame)

        # Convert the temperature list to a 24 x 32 image
        thermal = np.array(frame).reshape((24, 32))

        # Find current min/max temperatures
        min_temp = np.min(thermal)
        max_temp = np.max(thermal)

        # Convert temperatures into 0-255 image values
        if max_temp != min_temp:
            image = (thermal - min_temp) / (max_temp - min_temp)
        else:
            image = np.zeros_like(thermal)

        image = np.uint8(image * 255)

        # Enlarge the tiny 32x24 image
        image = cv2.resize(
            image,
            (640, 480),
            interpolation=cv2.INTER_CUBIC
        )

        # Apply thermal colors
        image = cv2.applyColorMap(
            image,
            cv2.COLORMAP_INFERNO
        )

        # Add minimum temperature information
        cv2.putText(
            image,
            f"Min: {min_temp:.1f} C",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Add maximum temperature information
        cv2.putText(
            image,
            f"Max: {max_temp:.1f} C",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        # Show thermal image
        cv2.imshow(
            "MLX90640 Thermal Camera",
            image
        )

        # Press Q to quit
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    except ValueError:
        # Occasionally the MLX90640 can miss a frame
        continue


cv2.destroyAllWindows()
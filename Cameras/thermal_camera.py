import time

import board
import busio
import adafruit_mlx90640


# Set up the I2C connection
i2c = busio.I2C(board.SCL, board.SDA)

# Connect to the MLX90640
mlx = adafruit_mlx90640.MLX90640(i2c)

# Start at a low refresh rate for a reliable first test
mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

# The MLX90640 produces 32 x 24 = 768 temperature values
frame = [0] * 768

print("MLX90640 connected!")
print("Reading temperatures... Press Ctrl+C to stop.")


while True:
    try:
        mlx.getFrame(frame)

        min_temp = min(frame)
        max_temp = max(frame)
        avg_temp = sum(frame) / len(frame)

        print(
            f"Min: {min_temp:.1f} C | "
            f"Max: {max_temp:.1f} C | "
            f"Average: {avg_temp:.1f} C"
        )

        time.sleep(0.5)

    except ValueError:
        # Occasionally an incomplete frame can occur
        continue
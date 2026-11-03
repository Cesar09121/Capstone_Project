"""
Benchmark the MLX90640 thermal camera at different refresh rates.
Measures how long each frame takes to read over I2C and how many reads fail.
Results are printed as a table and saved to a CSV file.
"""
import csv
import time
import board
import busio
import adafruit_mlx90640

# Refresh rates to test
REFRESH_RATES = {
    "2 Hz": adafruit_mlx90640.RefreshRate.REFRESH_2_HZ,
    "4 Hz": adafruit_mlx90640.RefreshRate.REFRESH_4_HZ,
    "8 Hz": adafruit_mlx90640.RefreshRate.REFRESH_8_HZ,
    "16 Hz": adafruit_mlx90640.RefreshRate.REFRESH_16_HZ,
}

FRAMES_PER_TEST = 20

RESULTS_FILE = "thermal_benchmark_results.csv"

def main():
    i2c = busio.I2C(board.SCL, board.SDA)
    mlx = adafruit_mlx90640.MLX90640(i2c)
    frame = [0.0] * 768

    results = []
    print(f"{'rate':>6} {'avg ms':>8} {'fps':>6} {'errors':>7} {'min C':>6} {'max C':>6}")

    for name, rate in REFRESH_RATES.items():
        mlx.refresh_rate = rate

        # Skip the first frame after changing the rate
        try:
            mlx.getFrame(frame)
        except (ValueError, RuntimeError, OSError):
            pass

        times = []
        errors = 0

        for _ in range(FRAMES_PER_TEST):
            start = time.time()

            try:
                mlx.getFrame(frame)
                times.append(time.time() - start)
            except (ValueError, RuntimeError, OSError):
                errors += 1

        if not times:
            print(f"{name:>6}  all reads failed")
            continue

        avg_ms = sum(times) / len(times) * 1000

        result = {
            "refresh_rate": name,
            "avg_ms": round(avg_ms, 1),
            "fps": round(1000 / avg_ms, 1),
            "errors": errors,
            "min_temp": round(min(frame), 1),
            "max_temp": round(max(frame), 1),
        }
        results.append(result)

        print(
            f"{name:>6} "
            f"{result['avg_ms']:>8} "
            f"{result['fps']:>6} "
            f"{result['errors']:>7} "
            f"{result['min_temp']:>6} "
            f"{result['max_temp']:>6}"
        )

    # Save the results for the report
    if results:
        with open(RESULTS_FILE, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)

        print()
        print(f"Saved results to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
import json
import random
import time
from datetime import datetime, timezone

DEVICE_ID = "robot_01"

def generate_reading():
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "acceleration_x": round(random.uniform(-1.5, 1.5), 3),
        "acceleration_y": round(random.uniform(-1.5, 1.5), 3),
        "acceleration_z": round(random.uniform(8.0, 11.0), 3),
        "angular_velocity_z": round(random.uniform(-0.5, 0.5), 3),
        "temperature": round(random.uniform(25.0, 35.0), 2),
        "humidity": round(random.uniform(40.0, 80.0), 2)
    }

if __name__ == "__main__":
    print("Robot sensor simulator started. Press Ctrl+C to stop.")

    try:
        while True:
            reading = generate_reading()
            print(json.dumps(reading, indent=2))
            print("-" * 50)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nSimulator stopped.")
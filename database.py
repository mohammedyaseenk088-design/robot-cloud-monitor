import sqlite3

DATABASE = "robot_data.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT,
            timestamp TEXT,
            acceleration_x REAL,
            acceleration_y REAL,
            acceleration_z REAL,
            angular_velocity_z REAL,
            temperature REAL,
            humidity REAL
        )
    """)

    connection.commit()
    connection.close()

    print("Database and telemetry table created successfully!")


if __name__ == "__main__":
    create_database()
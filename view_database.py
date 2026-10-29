import sqlite3

connection = sqlite3.connect("robot_data.db")
cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM telemetry")
count = cursor.fetchone()[0]

print(f"Total readings stored: {count}")

cursor.execute("""
    SELECT timestamp, temperature, humidity,
           acceleration_x, acceleration_y, acceleration_z
    FROM telemetry
    ORDER BY id DESC
    LIMIT 5
""")

print("\nLatest 5 readings:")
for row in cursor.fetchall():
    print(row)

connection.close()

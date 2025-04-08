from kafka import KafkaConsumer
import json
import psycopg
from datetime import datetime

consumer = KafkaConsumer(
    'iot-data',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='latest',
    group_id='iot-group'
)

conn = psycopg.connect("dbname=sensordata user=postgres password=postgres host=localhost")
cursor = conn.cursor()

print("Listening to iot-data...")

for msg in consumer:
    data = msg.value
    sensor_id = data.pop("sensor_id")
    timestamp = datetime.utcfromtimestamp(data.pop("timestamp"))

    for key, val in data.items():
        cursor.execute(
            "INSERT INTO iot_metrics (time, sensor_id, key, value) VALUES (%s, %s, %s, %s)",
            (timestamp, sensor_id, key, val)
        )
    conn.commit()
    print(f"Inserted data from {sensor_id} at {timestamp}")

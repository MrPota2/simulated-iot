import os
import time
from time import sleep

from kafka import KafkaConsumer
import json
import psycopg
from datetime import datetime

print("Starting iot-consumer...")
while True:
    try:
        # Attempt to connect to the PostgreSQL database
        consumer = KafkaConsumer(
            'iot-data',
            bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='iot-group'
        )
        break
    except Exception as e:
        print(f"No kafka brokers available for consumer, trying again in 5: {e}")
        time.sleep(5)


# Connect to PostgreSQL database
while True:
    try:
        conn = psycopg.connect("dbname=sensordata user=postgres password=postgres host=timescaledb")
        break
    except psycopg.OperationalError as e:
        print(f"Database connection failed: {e}")
        time.sleep(5)

cursor = conn.cursor()

print("Listening to iot-data...")
while True:
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
    time.sleep(5)
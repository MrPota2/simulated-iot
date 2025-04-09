import os
import time
from time import sleep

from kafka import KafkaConsumer
import json
import psycopg
from datetime import datetime

import signal
import sys

running = True

def handle_shutdown(signum, frame):
    global running
    print("Shutting down...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)

print("Starting iot-consumer...")
while running:
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
while running:
    try:
        conn = psycopg.connect("dbname=sensordata user=postgres password=postgres host=timescaledb")
        # Check if the connection is successful and the table exists
        with conn.cursor() as cursor:
            cursor.execute("""
                create table if not exists iot_metrics
                (
                    time      timestamp with time zone not null,
                    sensor_id text                     not null,
                    key       text                     not null,
                    value     double precision
                );
                
                alter table iot_metrics
                    owner to postgres;
            """)
            conn.commit()
        break
    except psycopg.OperationalError as e:
        print(f"Database connection failed: {e}")
        time.sleep(5)

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

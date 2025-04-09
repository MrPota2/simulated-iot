import os
import random
import time
import json
from kafka import KafkaProducer
import python_weather
import asyncio

from python_weather.forecast import Forecast


async def getweather() -> Forecast:
    # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
    async with python_weather.Client(unit=python_weather.METRIC) as client:
        # fetch a weather forecast from a city
        weather = await client.get('Oslo')

        # returns the current day's forecast temperature (int)
        return weather

print(f'Starting iot-producer on {os.environ["KAFKA_BOOTSTRAP"]} ')
while True:
    try:
        # Attempt to connect to the Kafka broker
        producer = KafkaProducer(
            bootstrap_servers=os.environ['KAFKA_BOOTSTRAP'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        break
    except Exception as e:
        print(f"No kafka brokers available for producer, trying again in 5: {e}")
        time.sleep(5)

sensor_configs = {
    "temp_sensor_01": lambda: {
        "temperature": asyncio.run(getweather()).temperature
    },
    "humidity_sensor_01": lambda: {
        "humidity": asyncio.run(getweather()).humidity
    },
    "vibration_sensor_01": lambda: {
        "vibration": asyncio.run(getweather()).precipitation
    },
    "air_quality_sensor_01": lambda: {
        "co2": asyncio.run(getweather()).pressure,
        "pm2_5": asyncio.run(getweather()).visibility
    }
}

while True:
    sensor_id = random.choice(list(sensor_configs.keys()))
    data = sensor_configs[sensor_id]()
    data["sensor_id"] = sensor_id
    data["timestamp"] = time.time()

    producer.send('iot-data', data)
    print("Sent:", data)
    time.sleep(0.1)
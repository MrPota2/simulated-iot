# 📶 Simulated IoT Processing Project

## 🔧 Setup Summary

- **Kafka:** Local setup via Docker Compose
- **Data Source:** Synthetic sensor data (temperature, humidity, etc.)
- **Consumer:** Python Kafka consumer with PostgreSQL (TimescaleDB)
- **Visualization:** Grafana dashboard (via Prometheus for Kafka metrics, TimescaleDB for sensor data)

---

## 🚀 Components

### 1. Kafka Producer
- Generates random sensor data (`sensor_id`, `temperature`, etc.)
- Sends data to Kafka topic `iot-data` at 10Hz

### 2. Kafka Consumer
- Subscribes to `iot-data`
- Parses messages, extracts metrics
- Stores data in TimescaleDB table: `iot_metrics`

| Field       | Type        | Description               |
|-------------|-------------|---------------------------|
| time        | TIMESTAMPTZ | Timestamp of reading      |
| sensor_id   | TEXT        | Sensor identifier         |
| key         | TEXT        | Metric name (e.g., temp)  |
| value       | DOUBLE PRECISION | Actual reading       |

### 3. Data Processing
- Aggregation (min/max/avg) handled in Grafana queries
- Optional: Python could do in-memory aggregation if needed

---

## 📊 Visualization

- **Grafana panels per metric**
- Realtime filtering by `sensor_id`
- Prometheus integration to monitor Kafka performance (`kafka_server_*` metrics)

---

## 📝 Notes

- All services containerized for easy setup
- TimescaleDB used for efficient time-series queries
- Prometheus used for Kafka introspection (via JMX Exporter)

---

## ✅ To Run

```bash
docker compose up --build -d
python producer.py  # in separate terminal


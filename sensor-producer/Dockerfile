FROM python:3.11-slim

# Set the working directory
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc build-essential \
 && rm -rf /var/lib/apt/lists/*


# Copy the requirements file into the container
COPY requirements.txt .
# Install the required packages

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

CMD ["sh", "-c", "trap 'kill 0' INT TERM; exec python3 -u iot-producer.py & exec python3 -u iot-consumer.py; wait"]

#!/bin/bash

# 1. Wait for Postgres to be ready
echo "Waiting for PostgreSQL to start..."
until pg_isready -h postgres -p 5432 -U your_user > /dev/null 2>&1; do
  echo "Postgres is unavailable - sleeping"
  sleep 2
done
echo "Postgres is up!"

# 2. Wait for Kafka to be reachable
echo "Waiting for Kafka to start..."
while ! nc -z kafka 9092; do
  echo "Kafka is unavailable - sleeping"
  sleep 2
done
echo "Kafka is up!"

# 3. Activate the virtual environment
if [ -d "/myvenv" ]; then
  echo "Activating virtual environment..."
  source /myvenv/bin/activate
else
  echo "Warning: Virtual environment not found at /myvenv"
fi



# 4. Start the Jupyter server
echo "Starting Jupyter Lab on port 8888..."
exec jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''

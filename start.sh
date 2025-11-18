#!/bin/bash

echo "Activating venv..."
source /myvenv/bin/activate

echo "Starting orchestrator (will wait for Kafka)..."
/app/wait-for-kafka.sh \
  /myvenv/bin/python /app/app/orchestrator.py --domain ocean

echo "Starting Jupyter Lab..."
exec jupyter lab \
  --ip=0.0.0.0 \
  --port=8888 \
  --no-browser \
  --allow-root \
  --NotebookApp.token=''

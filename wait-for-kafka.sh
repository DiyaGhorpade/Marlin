#!/bin/bash

echo "⏳ Waiting for Kafka (port)..."
while ! nc -z kafka 9092; do
  echo "Kafka port not open - sleeping"
  sleep 2
done

echo "Kafka port open — checking metadata..."

until /myvenv/bin/python - << 'EOF'
from kafka import KafkaProducer
try:
    p = KafkaProducer(bootstrap_servers="kafka:9092", request_timeout_ms=2000)
    p.partitions_for("__dummy__")
    p.close()
except:
    raise SystemExit(1)
EOF
do
  echo "Kafka metadata not ready - sleeping"
  sleep 2
done

echo "✅ Kafka is READY."
exec "$@"

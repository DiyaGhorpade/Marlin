from kafka import KafkaProducer
import json
import sys
from pipeline.common.schema_validation import validate_ocean_row
from pipeline.common.kafka_utils import get_producer

KAFKA_BROKER = "kafka:9092"
KAFKA_TOPIC = "oceanographic_data"


# Setup Kafka Producer
print(f"Connecting to Kafka broker at {KAFKA_BROKER}...")

try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
    )
    print("Kafka Producer connected.")
except Exception as e:
    print(f"Error connecting to Kafka: {e}")
    print("Ensure Kafka is running.")
    sys.exit(1)


# Produce messages from cleaned JSONL
def produce(cleaned_path):
    count = 0

    print(f"Reading cleaned data from: {cleaned_path}")

    with open(cleaned_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            # Parse JSON line
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                print("Skipping malformed JSON line.")
                continue

            # Validate ocean row structure
            try:
                validated = validate_ocean_row(row)
            except Exception as e:
                print("Skipped invalid ocean row:", e)
                continue

            # Send message
            try:
                producer.send(KAFKA_TOPIC, validated)
                count += 1
            except Exception as e:
                print("Kafka send failed:", e)

    producer.flush()
    print(f"Sent {count} messages to Kafka topic '{KAFKA_TOPIC}'.")

    return count


if __name__ == "__main__":
    cleaned_path = sys.argv[1] if len(sys.argv) > 1 else "/data/clean/ocean/cleaned.jsonl"
    produce(cleaned_path)

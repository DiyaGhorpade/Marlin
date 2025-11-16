import json
import sys

from pipeline.common.kafka_utils import get_producer
from pipeline.common.schema_validation import validate_dwc

KAFKA_TOPIC = "fisheries_data"


# -------------------------------------------------
# Initialize Kafka Producer
# -------------------------------------------------
print("Connecting to Kafka producer...")

try:
    producer = get_producer()
    print("Kafka Producer connected.")
except Exception as e:
    print(f"Error: Could not initialize Kafka producer: {e}")
    sys.exit(1)


# -------------------------------------------------
# Produce fisheries DWC messages
# -------------------------------------------------
def produce(cleaned_jsonl_path):
    count = 0

    print(f"Reading cleaned fisheries data from: {cleaned_jsonl_path}")

    with open(cleaned_jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            # Parse JSONL record
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print("Skipped malformed JSON line.")
                continue

            # Validate the DWC row
            # try:
            #     validate_dwc(rec)
            # except Exception as e:
            #     print("Skipped fisheries record:", e)
            #     continue

            # Send to Kafka
            try:
                producer.send(KAFKA_TOPIC, rec)
                count += 1
            except Exception as e:
                print("Kafka send failed:", e)

    producer.flush()
    print(f"Sent {count} messages to Kafka topic '{KAFKA_TOPIC}'.")

    return count


# -------------------------------------------------
# Entry Point
# -------------------------------------------------
if __name__ == "__main__":
    cleaned_jsonl_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "/data/clean/fisheries/cleaned_dwc.jsonl"
    )
    produce(cleaned_jsonl_path)

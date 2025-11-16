import json
import sys

from pipeline.common.kafka_utils import get_producer
# If you ever add validation like validate_ocean_row(), import it here:
# from pipeline.common.schema_validation import validate_biodiversity_row

KAFKA_TOPIC = "biodiversity_data"


# Show connection status
print("Connecting to Kafka producer...")

try:
    producer = get_producer()
    print("Kafka Producer connected.")
except Exception as e:
    print(f"Error: Failed to initialize Kafka producer: {e}")
    sys.exit(1)


def produce(cleaned_path):
    count = 0

    print(f"Reading cleaned biodiversity data from: {cleaned_path}")

    with open(cleaned_path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            # Parse JSON line
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print("Skipping malformed JSON line.")
                continue

            # Optional future validation structure:
            # try:
            #     rec = validate_biodiversity_row(rec)
            # except Exception as e:
            #     print("Skipped invalid biodiversity row:", e)
            #     continue

            # Send message to Kafka
            try:
                producer.send(KAFKA_TOPIC, rec)
                count += 1
            except Exception as e:
                print("Kafka send failed:", e)

    producer.flush()
    print(f"Sent {count} messages to Kafka topic '{KAFKA_TOPIC}'.")

    return count


if __name__ == "__main__":
    cleaned_path = sys.argv[1] if len(sys.argv) > 1 else "/data/clean/biodiversity/cleaned_dwc.jsonl"
    produce(cleaned_path)

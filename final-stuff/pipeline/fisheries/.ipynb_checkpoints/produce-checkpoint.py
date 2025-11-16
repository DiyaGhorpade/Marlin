import json
import sys
import os

from pipeline.common.kafka_utils import get_producer
from pipeline.common.schema_validation import validate_dwc


KAFKA_TOPIC = "fisheries_data"

print("Connecting to Kafka producer...")

try:
    producer = get_producer()
    print("Kafka Producer connected.")
except Exception as e:
    print(f"Error: Could not initialize Kafka producer: {e}")
    sys.exit(1)


def produce_file(path):
    """Produce messages for a single cleaned JSONL file."""
    count = 0
    print(f" → Reading cleaned file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                print("Skipped malformed JSON line.")
                continue

            try:
                validate_dwc(rec)
            except Exception as e:
                print("Skipped fisheries record:", e)
                continue

            try:
                producer.send(KAFKA_TOPIC, rec)
                count += 1
            except Exception as e:
                print("Kafka send failed:", e)

    print(f"   Sent {count} records from {os.path.basename(path)}")
    return count


def produce_all(clean_dir):
    """Scan directory and produce from all .jsonl files."""
    total = 0

    for fname in sorted(os.listdir(clean_dir)):
        if fname.lower().endswith(".jsonl"):
            fpath = os.path.join(clean_dir, fname)
            total += produce_file(fpath)

    producer.flush()
    print(f"\nTotal messages sent to Kafka topic '{KAFKA_TOPIC}': {total}")
    return total


if __name__ == "__main__":
    # default directory if no argument passed
    clean_dir = (
        sys.argv[1] if len(sys.argv) > 1 else "/data/clean/fisheries"
    )

    if not os.path.isdir(clean_dir):
        print(f"Error: {clean_dir} is not a directory.")
        sys.exit(1)

    produce_all(clean_dir)

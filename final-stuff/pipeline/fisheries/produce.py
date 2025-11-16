from pipeline.common.kafka_utils import get_producer
from pipeline.common.schema_validation import validate_dwc
import json
def produce(cleaned_jsonl_path):
    prod = get_producer()
    count = 0
    with open(cleaned_jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            rec = json.loads(line)
            try:
                validate_dwc(rec)
                prod.send('fisheries_data', rec)
                count += 1
            except Exception as e:
                print('Skipped fisheries record:', e)
    prod.flush()
    return count
if __name__ == '__main__':
    import sys
    print(produce(sys.argv[1] if len(sys.argv)>1 else '/data/clean/fisheries/cleaned_dwc.jsonl'))

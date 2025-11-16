from pipeline.common.kafka_utils import get_producer
import json
def produce(cleaned_path):
    prod = get_producer()
    count = 0
    with open(cleaned_path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            rec = json.loads(line)
            try:
                prod.send('biodiversity_data', rec)
                count += 1
            except Exception as e:
                print('Skipped biodiversity record', e)
    prod.flush()
    return count
if __name__=='__main__':
    import sys
    print(produce(sys.argv[1] if len(sys.argv)>1 else '/data/clean/biodiversity/filtered_dwc.jsonl'))

import os, time, json, psycopg2
from kafka import KafkaConsumer
from dotenv import load_dotenv
load_dotenv()
TOPIC='fisheries_data'
consumer = KafkaConsumer(TOPIC, bootstrap_servers='kafka:9092', value_deserializer=lambda m: json.loads(m.decode('utf-8')))
def get_db():
    for _ in range(8):
        try:
            return psycopg2.connect(dbname=os.getenv('POSTGRES_DB'), user=os.getenv('POSTGRES_USER'), password=os.getenv('POSTGRES_PASSWORD'), host=os.getenv('POSTGRES_HOST','postgres'))
        except Exception:
            time.sleep(2)
    raise RuntimeError('DB fail')
conn = get_db()
with conn.cursor() as cur:
    cur.execute("""CREATE TABLE IF NOT EXISTS fisheries_dwc(id SERIAL PRIMARY KEY, eventDate DATE, locality TEXT, measurementType TEXT, measurementValue DOUBLE PRECISION, measurementUnit TEXT, verbatimDepth TEXT, scientificName TEXT, occurrenceRemarks TEXT, source_file TEXT)""")
    conn.commit()
ins = """INSERT INTO fisheries_dwc(eventDate,locality,measurementType,measurementValue,measurementUnit,verbatimDepth,scientificName,occurrenceRemarks,source_file) VALUES (%(eventDate)s,%(locality)s,%(measurementType)s,%(measurementValue)s,%(measurementUnit)s,%(verbatimDepth)s,%(scientificName)s,%(occurrenceRemarks)s,%(source_file)s)"""
for msg in consumer:
    try:
        v = msg.value
        if v.get('eventDate'): v['eventDate'] = v['eventDate'][:10]
        with conn.cursor() as cur:
            cur.execute(ins, v)
            conn.commit()
    except Exception as e:
        conn.rollback()
        print('insert error', e)

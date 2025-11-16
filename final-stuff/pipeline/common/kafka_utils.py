import json
from kafka import KafkaProducer, KafkaConsumer
from typing import Any, Dict
KAFKA_BROKER = 'kafka:9092'

def get_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
    )

def get_consumer(topic, group_id):
    return KafkaConsumer(
        topic,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

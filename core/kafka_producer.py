"""
Kafka Producer - 뉴스 데이터 실시간 전송
"""
from kafka import KafkaProducer
import json

class NewsKafkaProducer:
    def __init__(self, bootstrap_servers='localhost:9092', topic='news-articles'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8')
        )
        self.topic = topic

    def send_article(self, article: dict):
        self.producer.send(self.topic, article)
        self.producer.flush() 
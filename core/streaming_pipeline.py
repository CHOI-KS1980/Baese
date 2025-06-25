"""
실시간 데이터 파이프라인 관리
"""
from core.kafka_producer import NewsKafkaProducer
from core.es_client import NewsESClient

class DataPipeline:
    def __init__(self):
        self.kafka = NewsKafkaProducer()
        self.es = NewsESClient()

    def process_and_index(self, article: dict):
        self.kafka.send_article(article)
        self.es.index_article(article) 
"""
Elasticsearch Client - 뉴스 데이터 인덱싱
"""
from elasticsearch import Elasticsearch

class NewsESClient:
    def __init__(self, hosts=['localhost:9200'], index='news-articles'):
        self.es = Elasticsearch(hosts)
        self.index = index

    def index_article(self, article: dict):
        self.es.index(index=self.index, body=article) 
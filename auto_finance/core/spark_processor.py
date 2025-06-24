"""
Spark Streaming - 실시간 뉴스 데이터 처리
"""
from pyspark.sql import SparkSession

def start_spark_streaming(kafka_bootstrap='localhost:9092', topic='news-articles'):
    spark = SparkSession.builder.appName("NewsStreamProcessor").getOrCreate()
    df = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", topic)
        .load()
    )
    # 예시: 단순 출력
    df.writeStream.format("console").start().awaitTermination() 
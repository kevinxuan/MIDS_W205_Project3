#!/usr/bin/env python
"""Extract events from kafka and write them to hdfs
"""
import json
import pyspark
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType, DecimalType


@udf('boolean')
def is_relevant(event_as_json):
    """udf for filtering events
    """
    event = json.loads(event_as_json)
    if event['event_type'] != 'default':
        return True
    return False


def event_schema():
    """
    root
    |-- Accept: string (nullable = true)
    |-- Host: string (nullable = true)
    |-- User-Agent: string (nullable = true)
    |-- event_type: string (nullable = true)
    |-- user: string (nullable = true)
    |-- price: decimal (nullable = true)
    |-- type: string (nullable = true)
    |-- fee: decimal (nullable = true)
    |-- name: string (nullable = true)
    |-- amount: decimal (nullable = true)
    """
    return StructType([
        StructField("Accept", StringType(), True),
        StructField("Host", StringType(), True),
        StructField("User-Agent", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("user", StringType(), True),
        StructField("price", DecimalType(), True),
        StructField("type", StringType(), True),
        StructField("fee", DecimalType(), True),
        StructField("name", StringType(), True),
        StructField("amount", DecimalType(), True),
    ])


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .enableHiveSupport() \
        .getOrCreate()

    raw_events = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka:29092") \
        .option("subscribe", "events") \
        .load()

    flattened_events = raw_events \
        .filter(is_relevant(raw_events.value.cast('string'))) \
        .select(raw_events.value.cast('string').alias('raw_event'),
                raw_events.timestamp.cast('string'),
                from_json(raw_events.value.cast('string'),
                          event_schema()).alias('json')) \
        .select('raw_event', 'timestamp', 'json.*')

    sink = flattened_events \
        .writeStream \
        .format("parquet") \
        .option("checkpointLocation", "/tmp/checkpoints_for_events") \
        .option("path", "/tmp/game_events") \
        .trigger(processingTime="10 seconds") \
        .start()
    
    sink.awaitTermination()


if __name__ == "__main__":
    main()

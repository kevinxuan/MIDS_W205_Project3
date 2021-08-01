"""Extract events from kafka and write them to hdfs
"""
import json
import pyspark
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import udf, from_json
from pyspark.sql.types import StructType, StructField, StringType, DecimalType


def main():
    """main
    """
    spark = SparkSession \
        .builder \
        .appName("ExtractEventsJob") \
        .enableHiveSupport() \
        .getOrCreate()

    spark.sql("""
        create external table if not exists hive_events (
            raw_event string,
            timestamp string,
            Accept string,
            Host string,
            User_Agent string,
            event_type string,
            user string,
            price decimal,
            type string,
            fee decimal,
            name string,
            amount decimal
        )
        stored as parquet
        location '/tmp/game_events/'
        """)

if __name__ == "__main__":
    main()
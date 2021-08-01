# W205 Project 3 - Group 4
#### Authors: Chetan Munugala, Kevin Xuan, Yao Chen, Yi Zhang

# Introduction

In this report, we want to setup our data pipeline starting from generating synthetic events to substitute the raw data from devices, logging events into kafka, and using Spark to land data to HDFS to utilizing Presto to query events from HDFS for insights. 

As data scientists in the game development company, we are interested in tracking whether a player joins a guild and how his or her cashes are earned in the game. Since we do not have raw data to start from, we will use `Apache Bench` to constantly generate different events for each user to replicate the process of streaming data. As we want to store these events into Kafka, we will have `Spark` to constantly extract data from streaming data, transform data to structured data, and save data into HDFS so that data scientists can use Presto to query data from the database to perform data analysis.

The objective of this project is to help us develop the skill to be able to build the entire data pipeline rather than ask data engineers to have the data ready for us. With this skillset and knowing what data we need in order to build a good predictive model which solves our business problem, we will directly access raw data, transform and store it into HDFS, and use distributed query programming language to obtain the table with the features we want.

# Procedure
### Setup Docker-Compose Environment
The first thing we need to do is to have the docker-compose environment ready. For this project, we will need zookeeper, kafka, cloudera, spark, presto, and mids container. With zookeeper and kafka container, we are able to create a topic under kafka and publish streaming data into the topic via MIDS container. Then we will go through transformation and filtering of data in the Spark container, and after that we will have cloudera container be ready to store large amount of streaming data. At the end, we have Presto container to query features in which we are interested to a structured table used for further data analysis and predictive model building.

To start all these clusters, run:
```
docker-compose up -d
```
and we will see
```
Creating network "project3-group-4_default" with the default driver
Creating project3-group-4_mids_1      ... done
Creating project3-group-4_zookeeper_1 ... done
Creating project3-group-4_cloudera_1  ... done
Creating project3-group-4_presto_1    ... done
Creating project3-group-4_kafka_1     ... done
Creating project3-group-4_spark_1     ... done
```
This indicates that we have successfully spinned up all the clusters we need for this project.


### Instrument the API logs
In the `game_api.py` python file, we have setup a web API so that we are able to capture the raw data from the devices who are calling making API calls. 

This is done in the [game_api.py](./game_api.py) file with the following events:
- default_event
- purchase_a_sword
- join_a_guild
- quit_guild
- get_paid

When one of these actions is being conducted on a device, the device will then call the corresponding API, and with the function `log_to_kafka` in the python file, the events will be sent to kafka.

To bring the server up, run 
```
docker-compose exec mids env FLASK_APP=/w205/project3-group-4/game_api.py flask run --host 0.0.0.0
```


### Create Kafka Topic
Next, we create a Kafka Topic named `events` to have the data temporary stored. To create the topic, run
```
docker-compose exec kafka kafka-topics --create --topic events --partitions 1 --replication-factor 1 --if-not-exists --zookeeper zookeeper:32181
```
Then we will see the following result

"Created topic events."

Then, open a new terminal and run the following:
```
docker-compose exec mids kafkacat -C -b kafka:29092 -t events -o beginning
```
to watch streaming events getting published into to Kafka every once while.

### Register Hive Table
This will mark the parquet files that we'll be landing in HDFS as a logical Hive table, so that it can be queries via Presto. We use [write_hive_table.py](./write_hive_table.py) to create external table `hive_events` and store as parquet in /tmp/game_events/.

To set this up, run:
```
docker-compose exec spark spark-submit /w205/project3-group-4/write_hive_table.py
```


### Processing events using Spark Streaming
To process the streaming events, including filtering out the irrelevant ones, we set up a pipeline using Spark Structured Streaming.

When submitted, the spark submit job will run every 10 seconds and land these streaming events into HDFS.

To start the process, run:
```
docker-compose exec spark spark-submit --conf "spark.sql.parquet.writeLegacyFormat=true" /w205/project3-group-4/write_event_stream.py
```
Notice the `spark.sql.parquet.writeLegacyFormat` configuration parameter is to ensure the format of parquet file is compatible with Hive, so data can be sucessfully read via Presto.


### Generating synthetic data using Apache Bench
For this project, we do not have actual devices which constantly generates streaming events. Hence, we will utilize Apache Bench to stimulate the data generating process so that we are able to test our data pipeline.

Now with the pipeline setup, we are finally ready to open the firehose of events. To generate events, we have put the generation of different combination of events in the shell script [generate_events.sh](./generate_events.sh).

Open another terminal and run the following:
```
while true; do
  bash generate_events.sh
  sleep 10
done
```
to generate streaming events.

Note: the command above will not terminate. Press `Ctrl+C` to abort the process of generation of streaming events.

### Checking whether data has been saved in HDFS
To check whether events are constantly landing into HDFS, open another terminal and
run the following:
```
docker-compose exec cloudera hadoop fs -ls /tmp/game_events/
```
every once while.

We should see more parquet files being generated if we keep Apache Bench running in the previous terminal.


### Querying the events using Presto
We can also see the growing data in the registered table `hive_events` via Presto.

First enter the Presto environment by running:
```
docker-compose exec presto presto --server presto:8080 --catalog hive --schema default
```

This gets into an interactive shell with Presto. To query the landed events, simply run:
```sql
describe hive_events;
```
and we will see a structured table with below columns and types:
```
   Column   |     Type      | Comment 
------------+---------------+---------
 raw_event  | varchar       |
 timestamp  | varchar       |
 accept     | varchar       |         
 host       | varchar       |         
 user_agent | varchar       |         
 event_type | varchar       |         
 user       | varchar       |         
 price      | decimal(10,0) |         
 type       | varchar       |         
 fee        | decimal(10,0) |         
 name       | varchar       |         
 amount     | decimal(10,0) |         

(12 rows)
```
In order to check if events are generated and kicked into HDFS with streaming, we can run:
```sql
select count(*) from hive_events;
```
As events are continuously being landed in HDFS, we can run the Presto `select count (*)` command above every once while, and we should see the count number of rows of data will be increasing over time.

Now, we can query the data we want from the table through Presto.


# Conclusion
By running the above commands, we are able to assemble a completed data pipeline to catch the events originally defined in the [game_api.py](./game_api.py) file. We first use the API server to kick in events into Kafka, and then leverage Spark streaming to land these events data into HDFS. We use the Apache Bench to stimulate the data generating process periodically and track the schema with hive metastore. Lastly, we are able to query the hive table with Presto and perform analysis on top of that.


# Files Submitted
- An analytics report (with a description of pipeline and some basic analysis)
- game_api.py
- generate_events.sh
- write_hive_table.py
- write_event_stream.py
- docker-compose.yml


import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from confluent_kafka import Consumer
import psycopg2
import time
import json
from datetime import datetime
from database.db_utils import get_connection
from database.db_queries import (
    CREATE_DB_CHECK,
    CREATE_DATABASE,
    CREATE_VEHICLE_DATA_TABLE,
    INSERT_VEHICLE_DATA,
)


def connect_server(dbname="bkk_traffic_tracker"):
    return get_connection(dbname)


def create_database():
    try:
        connection = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="localhost",
            port="5432",
        )
        connection.autocommit = True

        if connection:
            cursor = connection.cursor()

            cursor.execute(CREATE_DB_CHECK)
            exists = cursor.fetchone()

            if not exists:
                cursor.execute(CREATE_DATABASE)
                print("Database created successfully.")
            else:
                print("Database already exists.")

            cursor.close()
            connection.close()

            time.sleep(1)

    except Exception as e:
        print(f"Error creating the database: {e}")


def create_table():
    connection = connect_server()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(CREATE_VEHICLE_DATA_TABLE)
            print("Table is created successfully")
        except Exception as e:
            print(f"Error while creating table: {e}")
        finally:
            cursor.close()
            connection.close()


def insert_vehicle_data(vehicle_data):
    connection = connect_server()
    if connection:
        try:
            cursor = connection.cursor()
            for vehicle in vehicle_data:
                wheelchair_accessible = (
                    True if vehicle["wheelchair_accessible"] == 2 else False
                )

                vehicle_timestamp = datetime.strptime(
                    vehicle["timestamp"], "%Y-%m-%d %H:%M:%S"
                )

                cursor.execute(
                    INSERT_VEHICLE_DATA,
                    (
                        vehicle["trip_id"],
                        vehicle["route_id"],
                        vehicle["latitude"],
                        vehicle["longitude"],
                        vehicle["bearing"],
                        vehicle["speed"],
                        vehicle["current_stop_sequence"],
                        vehicle["current_status"],
                        vehicle_timestamp,
                        vehicle["stop_id"],
                        vehicle["vehicle_id"],
                        vehicle["vehicle_label"],
                        vehicle["license_plate"],
                        wheelchair_accessible,
                    ),
                )
            print("Data inserted/upgraded successfully")
        except Exception as e:
            print(f"Error while inserting/upgrading table: {e}")
        finally:
            cursor.close()
            connection.close()


def consume_kafka_messages(topic_name, kafka_server):
    consumer = Consumer(
        {
            "bootstrap.servers": kafka_server,
            "group.id": "vehicle-data-group",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    consumer.subscribe([topic_name])

    print("Consuming messages from Kafka...")
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            try:
                vehicle_data = json.loads(msg.value().decode("utf-8"))
                if isinstance(vehicle_data, dict):
                    vehicle_data = [vehicle_data]
                insert_vehicle_data(vehicle_data)
                consumer.commit(asynchronous=False)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Error processing message: {e}")
    finally:
        consumer.close()


if __name__ == "__main__":
    create_database()
    create_table()

    topic_name = "vehicle-data"
    kafka_server = "localhost:9092"

    consume_kafka_messages(topic_name, kafka_server)

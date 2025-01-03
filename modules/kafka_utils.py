from confluent_kafka import Producer, Consumer
from config import KAFKA_BOOTSTRAP_SERVERS


def get_producer_config():
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "retries": 5,
    }


def get_consumer_config():
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "vehicle-data-group",
        "auto.offset.reset": "earliest",
        "retries": 5,
    }


def create_kafka_producer():
    return Producer(get_producer_config())


def create_kafka_consumer():
    return Consumer(get_consumer_config())

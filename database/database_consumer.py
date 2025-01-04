from confluent_kafka import Producer, Consumer
from config import KAFKA_BOOTSTRAP_SERVERS


def get_producer_config():
    """
    Returns the configuration dictionary for a Kafka producer.

    The configuration includes the bootstrap servers and the number of retries
    for sending messages.

    Returns:
        dict: A dictionary containing the Kafka producer configuration.
    """
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "retries": 5,
    }


def get_consumer_config():
    """
    Generate the configuration dictionary for a Kafka consumer.

    Returns:
        dict: A dictionary containing the configuration settings for a Kafka consumer,
        including bootstrap servers, group ID, offset reset policy, and retry count.
    """
    return {
        "bootstrap.servers": KAFKA_BOOTSTRAP_SERVERS,
        "group.id": "vehicle-data-group",
        "auto.offset.reset": "earliest",
        "retries": 5,
    }


def create_kafka_producer():
    """
    Creates and returns a Kafka producer instance.

    The producer is configured using the settings provided by the
    get_producer_config function.

    Returns:
        Producer: An instance of the Kafka producer.
    """
    return Producer(get_producer_config())


def create_kafka_consumer():
    """
    Create a Kafka consumer instance using the predefined configuration.

    Returns:
        Consumer: An instance of the Kafka Consumer configured with settings
        such as bootstrap servers, group ID, and offset reset policy.
    """
    return Consumer(get_consumer_config())

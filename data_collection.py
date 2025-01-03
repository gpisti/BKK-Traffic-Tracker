from config import API_KEY
import requests
import json
from encoders.gtfs_realtime_pb2 import FeedMessage
from time import sleep
from datetime import datetime, timezone
from modules.kafka_utils import create_kafka_producer

producer = create_kafka_producer()


def fetch_data(API_KEY=API_KEY):
    """
    Fetch GTFS vehicle position data from the BKK API.

    :param API_KEY: BKK API key string. Defaults to the one in config.py.
    :return: A list of dictionaries with vehicle position information.
    """
    try:
        vehicle_position_response = requests.get(
            f"https://go.bkk.hu/api/query/v1/ws/gtfs-rt/full/VehiclePositions.pb?key={API_KEY}"
        )
        vehicle_position_response.raise_for_status()

        feed = FeedMessage()
        feed.ParseFromString(vehicle_position_response.content)

        vehicle_data = []

        if feed.IsInitialized():
            for entity in feed.entity:
                if entity.HasField("vehicle"):
                    vehicle = entity.vehicle
                    vehicle_info = extract_vehicle_info(vehicle)
                    if vehicle_info:
                        vehicle_data.append(vehicle_info)

        else:
            print("Vehicle Position data is not fully initialized.")

        return vehicle_data

    except requests.exceptions.RequestException as e:
        print(f"Error while fetching data: {e}\n" + "-" * 30)
        return []


def extract_vehicle_info(vehicle):
    """
    Extract relevant vehicle position data into a dictionary.

    :param vehicle: The GTFS vehicle object.
    :return: Dictionary with keys like trip_id, route_id, latitude, speed, etc.
    """
    
    if vehicle.trip.route_id == "9999":
        return
    
    vehicle_info = {
        "trip_id": vehicle.trip.trip_id,
        "route_id": vehicle.trip.route_id,
        "latitude": vehicle.position.latitude,
        "longitude": vehicle.position.longitude,
        "bearing": vehicle.position.bearing,
        "speed": vehicle.position.speed * 3.6,
        "current_stop_sequence": vehicle.current_stop_sequence,
        "current_status": vehicle.current_status,
        "timestamp": datetime.fromtimestamp(
            vehicle.timestamp, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S"),
        "stop_id": vehicle.stop_id,
        "vehicle_id": vehicle.vehicle.id,
        "vehicle_label": vehicle.vehicle.label,
        "license_plate": vehicle.vehicle.license_plate,
        "wheelchair_accessible": vehicle.vehicle.wheelchair_accessible,
    }
    return vehicle_info


def send_to_kafka(vehicle_data):
    """
    Send fetched vehicle data to Kafka.

    :param vehicle_data: List of vehicle data dictionaries.
    """
    for vehicle in vehicle_data:
        vehicle_json = json.dumps(vehicle)
        try:
            producer.produce("vehicle-data", value=vehicle_json)
            producer.flush()
            print(f"Sent vehicle data to Kafka: {vehicle}")
        except Exception as e:
            print(f"Error sending to Kafka: {e}")


def main():
    while True:
        print("Fetching data from API...")
        vehicle_data = fetch_data()
        if vehicle_data:
            print("Sending data to Kafka...")
            send_to_kafka(vehicle_data)
        else:
            print("No data fetched.")
        sleep(10)


if __name__ == "__main__":
    main()

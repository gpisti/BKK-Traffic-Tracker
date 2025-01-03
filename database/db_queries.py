CREATE_DB_CHECK = """
SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'bkk_traffic_tracker';
"""

CREATE_DATABASE = """
CREATE DATABASE bkk_traffic_tracker;
"""

CREATE_VEHICLE_DATA_TABLE = """
CREATE TABLE IF NOT EXISTS vehicle_data (
    trip_id VARCHAR(255),
    route_id VARCHAR(255),
    latitude FLOAT,
    longitude FLOAT,
    bearing FLOAT,
    speed FLOAT,
    current_stop_sequence INT,
    current_status VARCHAR(255),
    timestamp TIMESTAMP WITH TIME ZONE,
    stop_id VARCHAR(255),
    vehicle_id VARCHAR(255),
    vehicle_label VARCHAR(255),
    license_plate VARCHAR(255),
    wheelchair_accessible BOOLEAN,
    PRIMARY KEY (vehicle_id, timestamp)
);
"""

INSERT_VEHICLE_DATA = """
INSERT INTO vehicle_data (
    trip_id, route_id, latitude, longitude, bearing, speed,
    current_stop_sequence, current_status, timestamp, stop_id,
    vehicle_id, vehicle_label, license_plate, wheelchair_accessible
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (vehicle_id, timestamp) DO UPDATE
SET latitude = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude,
    bearing = EXCLUDED.bearing,
    speed = EXCLUDED.speed,
    current_stop_sequence = EXCLUDED.current_stop_sequence,
    current_status = EXCLUDED.current_status,
    stop_id = EXCLUDED.stop_id,
    vehicle_label = EXCLUDED.vehicle_label,
    license_plate = EXCLUDED.license_plate,
    wheelchair_accessible = EXCLUDED.wheelchair_accessible;
"""

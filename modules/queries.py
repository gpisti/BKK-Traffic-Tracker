GET_DISTINCT_ROUTES = """
SELECT DISTINCT route_id FROM vehicle_data
"""

TRAFFIC_HEATMAP_BASE = """
SELECT latitude, longitude, COUNT(DISTINCT vehicle_id) AS traffic_count
FROM vehicle_data
WHERE latitude IS NOT NULL AND longitude IS NOT NULL
"""

KPIS_BASE = """
SELECT route_id,
       AVG(speed) AS avg_speed,
       COUNT(DISTINCT vehicle_id) AS traffic_count
FROM vehicle_data
"""

ROUTE_PERFORMANCE_BASE = """
SELECT route_id,
       AVG(speed) AS avg_speed,
       COUNT(DISTINCT vehicle_id) AS traffic_count
FROM vehicle_data
"""

PEAK_NONPEAK_BASE = """
SELECT EXTRACT(HOUR FROM timestamp) AS hour,
       AVG(speed) AS avg_speed,
       COUNT(*) AS traffic_count
FROM vehicle_data
"""

ENV_IMPACT_BASE = """
SELECT route_id,
       COUNT(vehicle_id) AS traffic_count,
       AVG(speed) AS avg_speed
FROM vehicle_data
"""

CORRELATION_BASE = """
SELECT speed, COUNT(*) AS traffic_count
FROM vehicle_data
"""

ROUTE_OPTIMIZATION_BASE = """
SELECT route_id, AVG(speed) AS avg_speed
FROM vehicle_data
"""

TRAFFIC_BY_DAY_OF_WEEK_BASE = """
SELECT EXTRACT(DOW FROM timestamp) AS day_of_week,
       COUNT(*) AS traffic_count
FROM vehicle_data
"""

SPEED_DISTRIBUTION_BASE = """
SELECT route_id, speed
FROM vehicle_data
WHERE speed > 0
"""

VEHICLE_COUNT_BASE = """
SELECT route_id, COUNT(*) AS vehicle_count
FROM vehicle_data
"""

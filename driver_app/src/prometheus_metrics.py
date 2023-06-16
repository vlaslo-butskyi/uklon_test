from prometheus_client import Counter, multiprocess
from prometheus_client.core import CollectorRegistry


REGISTRY = CollectorRegistry()
multiprocess.MultiProcessCollector(REGISTRY, path="/tmp")

metrics_prefix = "service_"
request_counter = Counter(f"{metrics_prefix}requests_total", "Total number of requests")
coordinates_counter = Counter(f"{metrics_prefix}coordinates_total", "Total number of received coordinates")
unique_drivers_counter = Counter(f"{metrics_prefix}unique_drivers_total", "Total number of unique drivers")
speeding_coordinates_counter = Counter(
    f"{metrics_prefix}speeding_coordinates_total", "Total number of coordinates with speeding"
)
abnormal_altitude_counter = Counter(
    f"{metrics_prefix}abnormal_altitude_total", "Total number of coordinates with abnormal altitude"
)
table_records_counter = Counter(f"{metrics_prefix}table_records_total", "Total number of records in the table")

REGISTRY.register(request_counter)
REGISTRY.register(coordinates_counter)
REGISTRY.register(unique_drivers_counter)
REGISTRY.register(speeding_coordinates_counter)
REGISTRY.register(abnormal_altitude_counter)
REGISTRY.register(table_records_counter)

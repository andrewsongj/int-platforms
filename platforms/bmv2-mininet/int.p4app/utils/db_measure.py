from influxdb import InfluxDBClient
import time

# Configuration
url = "http://localhost:8086"  # Replace with your InfluxDB URL
token = "your-token"  # Replace with your token
org = "your-org"  # Replace with your organization
bucket = "your-bucket"  # Replace with your bucket


# Create a client
def influx_client():
    host = "localhost"
    port = 8086
    user = "int"
    password = "gn4intp4"
    dbname = "int_telemetry_db"

    client = InfluxDBClient(host, port, user, password, dbname)
    return client


client = influx_client()
# dbs = client.get_list_database()
# print(dbs)
query = "SELECT hop_delay FROM \"int_telemetry\" WHERE time >= '2023-12-03T22:33:00Z' AND time <= '2023-12-03T22:35:00Z'"
# query = 'SELECT hop_delay FROM "int_telemetry" ORDER BY time DESC LIMIT 1'
# Earliest time: 2023-11-27T06:00:26.992390Z
# Latest time: 2023-12-02T04:58:42.569723Z

num_iterations = [1, 10]
times = []
for _ in range(5):
    trial = []
    for i in num_iterations:
        start_time = time.time()
        for _ in range(i):
            results = client.query(query)
        end_time = time.time()
        trial.append(end_time - start_time)
    times.append(trial)
print(times)
# print(count)
# measurements = client.query("SHOW MEASUREMENTS")
# print(measurements)

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
dbs = client.get_list_database()
print(dbs)
count = client.query("SELECT * FROM int_telemetry")
print(count)
measurements = client.query("SHOW MEASUREMENTS")
print(measurements)

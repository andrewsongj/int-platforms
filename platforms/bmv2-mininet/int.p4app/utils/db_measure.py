from influxdb import InfluxDBClient
import time
import psycopg2

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


def pg_client():
    conn = psycopg2.connect(
        host="localhost",
        database="int_telemetry_db",
        user="andrew",
        password="andrew",
        port=5432,
    )

    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("***********************PG VERSION " + str(record))
    return conn


# client = influx_client()
# dbs = client.get_list_database()
# print(dbs)
# count = client.query("SELECT * FROM int_telemetry")
# print(count)
# measurements = client.query("SHOW MEASUREMENTS")
# print(measurements)
pg = pg_client()

from influxdb import InfluxDBClient
import time
import psycopg2
import json

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
    # cursor.execute("SELECT version();")
    # record = cursor.fetchone()
    # print("***********************PG VERSION " + str(record))
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS int_telemetry (
           id SERIAL PRIMARY KEY,
           data JSONB
       );
    """
    )
    conn.commit()

    return conn, cursor


# client = influx_client()
# dbs = client.get_list_database()
# print(dbs)
# count = client.query("SELECT * FROM int_telemetry")
# print(count)
# measurements = client.query("SHOW MEASUREMENTS")
# print(measurements)
conn, cursor = pg_client()

data_points = [
    {
        "measurement": "cpu_load_short",
        "tags": {"host": "server01", "region": "us-west"},
        "time": "2023-12-09T10:00:00Z",
        "fields": {"value": 0.64},
    },
    {
        "measurement": "temperature",
        "tags": {"device": "thermostat", "room": "living_room"},
        "time": "2023-12-09T10:05:00Z",
        "fields": {"value": 22.5},
    },
    {
        "measurement": "humidity",
        "tags": {"device": "hygrometer", "room": "kitchen"},
        "time": "2023-12-09T10:10:00Z",
        "fields": {"value": 60},
    },
]

# for entry in data_points:
#     cursor.execute(
#         """
#         INSERT INTO int_telemetry (data)
#         VALUES (%s)
#     """,
#         (json.dumps(entry),),
#     )
# conn.commit()

# cursor.execute("SELECT * FROM int_telemetry WHERE id BETWEEN 10 AND 414807;")
# record = cursor.fetchall()
# for r in record:
#     print("*********************** " + str(r))

num_iterations = [1, 10, 100]
times = []
for _ in range(5):
    trial = []
    for i in num_iterations:
        start_time = time.time()
        for _ in range(i):
            cursor.execute(
                """SELECT * FROM int_telemetry WHERE id BETWEEN 10 AND 414807;"""
            )
            records = cursor.fetchall()
        end_time = time.time()
        trial.append(end_time - start_time)
    times.append(trial)
print(times)

from collections import deque
import random
from datetime import datetime


class SensorData:
    def __init__(self):
        self.min_temp = 18.0
        self.max_temp = 26.0
        self.min_humidity = 30.0
        self.max_humidity = 65.0

    def generate_reading(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "temperature": round(random.uniform(self.min_temp, self.max_temp), 1),
            "humidity": round(random.uniform(self.min_humidity, self.max_humidity), 1),
            "status": random.choice(["normal", "warning", "critical"])
        }


# Store recent readings for charts
recent_readings = deque(maxlen=20)


# def db_connect():
#     import duckdb
#     """Connect to the DuckDB database and return a success message."""
#     try:
#         conn = duckdb.connect('data/main.db')
#         # return {"status": "success", "message": "Connected to the database."}
#         return conn
#     except Exception as e:
#         logger.error(f"Database connection failed: {e}")
#         return {"status": "error", "message": str(e)}


# def db_disconnect(con):
#     """Disconnect from the DuckDB database."""
#     try:
#         con.close()
#         return {"status": "success", "message": "Disconnected from the database."}  
#     except Exception as e:
#         logger.error(f"Database disconnection failed: {e}")
#         return {"status": "error", "message": str(e)}


def get_owner_list(con):
    """Get the owner list from the database."""
    try:
        result = con.sql("SELECT * FROM owner").fetchall()
        # return [dict(row) for row in result]
        return result
    except Exception as e:
        # logger.error(f"Failed to fetch owner list: {e}")
        return [e]

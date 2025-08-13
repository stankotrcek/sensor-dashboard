import duckdb

DATABASE_PATH = "data/main.db"


def get_connection():
    conn = duckdb.connect(DATABASE_PATH)
    return conn


def init_db():
    # conn = get_connection()
    # cursor = conn.cursor()
    # cursor.execute("""
    #     CREATE TABLE IF NOT EXISTS users (
    #         id INTEGER PRIMARY KEY AUTOINCREMENT,
    #         name TEXT NOT NULL,
    #         email TEXT UNIQUE NOT NULL
    #     )
    # """)
    # conn.commit()
    # conn.close()
    ...
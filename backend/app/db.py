import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "flightbadges"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
        host=os.getenv("POSTGRES_HOST", "db"),
        port=5432
    )
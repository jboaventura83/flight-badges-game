from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
from models import Airport

app = FastAPI()

origins = [
    "http://localhost:3000",  # frontend React dev server
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return psycopg2.connect(
        dbname="flightbadges",
        user="postgres",
        password="postgres",
        host="db"
    )

@app.get("/airports/", response_model=List[Airport])
def list_airports():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT iata_code, name, iso_country, latitude_deg, longitude_deg
        FROM airports
        WHERE iata_code IS NOT NULL AND iata_code <> ''
        LIMIT 100
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows
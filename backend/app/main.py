from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel
from models import Airport, VisitRequest

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

class ClickRequest(BaseModel):
    latitude: float
    longitude: float

@app.post("/nearest-airport/")
def nearest_airport(req: ClickRequest):
    conn = get_db_connection()
    cur = conn.cursor()

    query = """
        SELECT iata_code, name, iso_country,
        ST_Distance(
            geography(ST_MakePoint(longitude_deg, latitude_deg)),
            geography(ST_MakePoint(%s, %s))
        ) AS distance
        FROM airports
        ORDER BY distance ASC
        LIMIT 1;
    """

    cur.execute(query, (req.longitude, req.latitude))
    result = cur.fetchone()
    conn.close()

    if result:
        return {
            "iata_code": result[0],
            "name": result[1],
            "country": result[2],
            "distance_meters": result[3]
        }
    else:
        return {"message": "Nenhum aeroporto encontrado."}


@app.get("/airports/", response_model=List[Airport])
def list_airports():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT iata_code, name, iso_country, latitude_deg, longitude_deg
        FROM airports
        WHERE iata_code IS NOT NULL AND iata_code <> ''
        LIMIT 1000
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return rows

@app.post("/visit")
def mark_visited(visit: VisitRequest):
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO user_airports (user_name, iata_code)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
        """, (visit.user_name, visit.iata_code))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

    return {"message": "Aeroporto registrado com sucesso!"}

@app.get("/visited/{user_name}")
def get_visited(user_name: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT iata_code FROM user_airports
        WHERE user_name = %s
    """, (user_name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [r[0] for r in rows]
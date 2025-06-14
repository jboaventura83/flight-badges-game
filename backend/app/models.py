from pydantic import BaseModel

class Airport(BaseModel):
    iata_code: str
    name: str
    iso_country: str
    latitude_deg: float
    longitude_deg: float

class VisitRequest(BaseModel):
    user_name: str
    iata_code: str
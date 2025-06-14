CREATE EXTENSION IF NOT EXISTS postgis;

DROP TABLE IF EXISTS airports;

CREATE TABLE airports (
    id SERIAL PRIMARY KEY,
    iata_code TEXT,
    name TEXT,
    iso_country TEXT,
    latitude_deg DOUBLE PRECISION,
    longitude_deg DOUBLE PRECISION,
    geom GEOGRAPHY(Point, 4326)
);

-- Tabela temporária só para importação completa
CREATE TEMP TABLE tmp_airports (
    id INT,
    ident TEXT,
    type TEXT,
    name TEXT,
    latitude_deg DOUBLE PRECISION,
    longitude_deg DOUBLE PRECISION,
    elevation_ft TEXT,
    continent TEXT,
    iso_country TEXT,
    iso_region TEXT,
    municipality TEXT,
    scheduled_service TEXT,
    icao_code TEXT,
    iata_code TEXT,
    gps_code TEXT,
    local_code TEXT,
    home_link TEXT,
    wikipedia_link TEXT,
    keywords TEXT
);

-- Importa o CSV na tabela temporária
COPY tmp_airports FROM '/docker-entrypoint-initdb.d/airports.csv' DELIMITER ',' CSV HEADER;

-- Insere apenas os campos que nos interessam
INSERT INTO airports (iata_code, name, iso_country, latitude_deg, longitude_deg)
SELECT iata_code, name, iso_country, latitude_deg, longitude_deg
FROM tmp_airports
WHERE iata_code IS NOT NULL AND iata_code <> '';

-- Atualiza a coluna geográfica
UPDATE airports
SET geom = ST_SetSRID(ST_MakePoint(longitude_deg, latitude_deg), 4326)::GEOGRAPHY;
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Ícone customizado para o Marker (fallback padrão do Leaflet)
const airportIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.3/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function Map() {
  const [airports, setAirports] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/airports/")
      .then((res) => {
        if (!res.ok) throw new Error("Falha ao carregar aeroportos");
        return res.json();
      })
      .then((data) => setAirports(data))
      .catch((err) => setError(err.message));
  }, []);

  return (
    <div style={{ height: "100vh", width: "100vw" }}>
      {error && (
        <div
          style={{
            position: "absolute",
            zIndex: 1000,
            background: "rgba(255,0,0,0.8)",
            color: "white",
            padding: "10px",
            top: 10,
            left: 10,
            borderRadius: 4,
          }}
        >
          {error}
        </div>
      )}

      <MapContainer center={[20, 0]} zoom={2} style={{ height: "100%", width: "100%" }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

        {airports.length === 0 && !error && (
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              background: "rgba(0,0,0,0.6)",
              color: "white",
              padding: "12px 20px",
              borderRadius: 6,
              pointerEvents: "none",
              zIndex: 1000,
              fontSize: 18,
            }}
          >
            Carregando aeroportos...
          </div>
        )}

        {airports.map(({ iata_code, name, iso_country, latitude_deg, longitude_deg }) => (
          <Marker
            key={iata_code || `${latitude_deg}-${longitude_deg}`} // fallback key caso iata_code ausente
            position={[latitude_deg, longitude_deg]}
            icon={airportIcon}
          >
            <Popup>
              <strong>{name}</strong> ({iata_code}) <br />
              País: {iso_country}
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
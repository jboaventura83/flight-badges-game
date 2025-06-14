import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from "react-leaflet";
import MarkerClusterGroup from 'react-leaflet-cluster';
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Ícones
const visitedIcon = new L.Icon({
  iconUrl: "https://cdn-icons-png.flaticon.com/512/190/190411.png",
  iconSize: [30, 30],
  iconAnchor: [15, 30],
  popupAnchor: [0, -30],
});

const defaultIcon = new L.Icon({
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
  const [visited, setVisited] = useState([]);
  const [user, setUser] = useState("");
  const [loading, setLoading] = useState(false);
  const mapRef = useRef();

  // Load user
  useEffect(() => {
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      setUser(savedUser);
    } else {
      const inputUser = prompt("Digite seu nome:");
      localStorage.setItem("user", inputUser);
      setUser(inputUser);
    }
  }, []);

  // Load visited
  useEffect(() => {
    if (user) {
      fetch(`http://localhost:8000/visited/${user}`)
        .then((res) => res.json())
        .then((data) => setVisited(data));
    }
  }, [user]);

  const fetchAirportsInBounds = (bounds) => {
    const { _southWest, _northEast } = bounds;
    const url = `http://localhost:8000/airports_in_bounds/?min_lat=${_southWest.lat}&max_lat=${_northEast.lat}&min_lon=${_southWest.lng}&max_lon=${_northEast.lng}`;
    setLoading(true);
    fetch(url)
      .then((res) => res.json())
      .then((data) => setAirports(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  let debounceTimer = null;

  const MapEventHandler = () => {
    const map = useMapEvents({
      moveend: () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          const bounds = map.getBounds();
          fetchAirportsInBounds(bounds);
        }, 300);
      }
    });
    return null;
  };

  const handleVisit = (iata_code) => {
    fetch("http://localhost:8000/visit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_name: user, iata_code }),
    })
      .then((res) => {
        if (res.ok) {
          setVisited((prev) => [...prev, iata_code]);
        } else {
          alert("Erro ao registrar visita.");
        }
      })
      .catch(console.error);
  };

  return (
    <div style={{ height: "100vh", width: "100vw" }}>
      {loading && (
        <div style={{
          position: 'absolute', top: 10, left: '50%', transform: 'translateX(-50%)',
          backgroundColor: '#000000aa', padding: '8px 16px',
          color: 'white', borderRadius: '8px', zIndex: 1000
        }}>
          Carregando aeroportos...
        </div>
      )}

      <MapContainer 
        center={[20, 0]} 
        zoom={2} 
        style={{ height: "100%", width: "100%" }}
        whenCreated={mapInstance => { mapRef.current = mapInstance }}
      >
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <MapEventHandler />

        <MarkerClusterGroup chunkedLoading>
          {airports.map(({ iata_code, name, iso_country, latitude_deg, longitude_deg }) => {
            const isVisited = visited.includes(iata_code);
            return (
              <Marker
                key={iata_code}
                position={[latitude_deg, longitude_deg]}
                icon={isVisited ? visitedIcon : defaultIcon}
              >
                <Popup>
                  <strong>{name}</strong> ({iata_code})<br />
                  País: {iso_country} <br />
                  {isVisited ? (
                    <span style={{ color: "green" }}>Já visitado ✅</span>
                  ) : (
                    <button onClick={() => handleVisit(iata_code)}>Marcar como visitado</button>
                  )}
                </Popup>
              </Marker>
            );
          })}
        </MarkerClusterGroup>

      </MapContainer>
    </div>
  );
}
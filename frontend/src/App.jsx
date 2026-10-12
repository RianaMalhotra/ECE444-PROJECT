
import { useEffect, useState } from "react";
import { fetchRiskAreas } from "./services/riskApi";
import { MapContainer, TileLayer, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const riskColors = {
  HIGH: "red",
  MODERATE: "orange",
  LOW: "green",
};

function App() {
  const [riskAreas, setRiskAreas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dataSource, setDataSource] = useState(null);

  useEffect(() => {
    let active = true;

    async function loadRiskAreas() {
      try {
        const result = await fetchRiskAreas();

        if (!active) return;

        setRiskAreas(result.data);
        setDataSource(result.source);
        setError(null);
      } catch (err) {
        if (!active) return;

        setRiskAreas([]);
        setError(err.message || "Unable to load wildfire risk data.");
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadRiskAreas();

    return () => {
      active = false;
    };
  }, []);

  return (
    <div>
      <h1>Wildfire Early Detection & Risk Assessment</h1>

      {loading && (
        <p>Loading wildfire risk data...</p>
      )}

      {error && (
        <p role="alert" style={{ color: "red" }}>
          Risk data unavailable: {error}
        </p>
      )}

      {dataSource === "mock" && !error && (
        <p>Demo data — not live wildfire risk</p>
      )}

      <MapContainer
        center={[45.4, -77.5]}
        zoom={7}
        style={{ height: "80vh", width: "100%" }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {riskAreas.map((area) => {
          const color = riskColors[area.risk_level] || "gray";

          return (
            <Circle
              key={area.id}
              center={[area.latitude, area.longitude]}
              radius={12000}
              pathOptions={{
                color: color,
                fillColor: color,
                fillOpacity: 0.5,
              }}
            >
              <Popup>
                <strong>
                  Wildfire Risk: {area.risk_level}
                </strong>

                <p>
                  Latitude: {area.latitude}
                  <br />
                  Longitude: {area.longitude}
                </p>

                {dataSource === "mock" && (
                  <p>Demo data — not live wildfire risk</p>
                )}
              </Popup>
            </Circle>
          );
        })}
      </MapContainer>
    </div>
  );
}

export default App;

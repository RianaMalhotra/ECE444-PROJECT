import { MapContainer, TileLayer, Circle, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const riskAreas = [
  { id: 1, lat: 45.42, lng: -75.69, risk: "HIGH", color: "red" },
  { id: 2, lat: 45.60, lng: -78.40, risk: "MODERATE", color: "orange" },
  { id: 3, lat: 44.20, lng: -79.10, risk: "LOW", color: "green" }
];

function App() {
  return (
    <div>
      <h1>Wildfire Early Detection & Risk Assessment</h1>

      <MapContainer
        center={[45.4, -77.5]}
        zoom={7}
        style={{ height: "80vh", width: "100%" }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {riskAreas.map((area) => (
          <Circle
            key={area.id}
            center={[area.lat, area.lng]}
            radius={12000}
            pathOptions={{
              color: area.color,
              fillColor: area.color,
              fillOpacity: 0.5
            }}
          >
            <Popup>
              Wildfire Risk: {area.risk}
              <p>Demo data — not live wildfire risk</p>
            </Popup>
          </Circle>
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
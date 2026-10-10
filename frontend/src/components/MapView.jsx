import {
  MapContainer,
  TileLayer,
  Circle,
  Popup
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import { mockRiskData } from "../data/mockRiskData";

function getRiskColor(score) {
  if (score >= 70) return "#dc2626";
  if (score >= 40) return "#f59e0b";
  return "#16a34a";
}

export default function MapView() {
  return (
    <MapContainer
      center={[44.8, -78.5]}
      zoom={7}
      style={{ height: "650px", width: "100%" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {mockRiskData.map((area) => (
        <Circle
          key={area.id}
          center={[area.latitude, area.longitude]}
          radius={15000}
          pathOptions={{
            color: getRiskColor(area.riskScore),
            fillColor: getRiskColor(area.riskScore),
            fillOpacity: 0.45
          }}
        >
          <Popup>
            <h3>{area.name}</h3>
            <p>Wildfire Risk: {area.riskLevel}</p>
            <p>Risk Score: {area.riskScore}/100</p>
            <p>Demo data only</p>
          </Popup>
        </Circle>
      ))}
    </MapContainer>
  );
}
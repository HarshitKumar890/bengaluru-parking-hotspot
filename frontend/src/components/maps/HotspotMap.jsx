import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import HotspotPopup from "./HotspotPopup";

export default function HotspotMap({
  hotspots,
}) {
  return (
    <MapContainer
      center={[
        12.9716,
        77.5946,
      ]}
      zoom={11}
      style={{
        height: "700px",
        width: "100%",
      }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {hotspots.map(
        (hotspot, index) => {
          if (
            !hotspot.cell_lat ||
            !hotspot.cell_lon
          )
            return null;

          return (
            <Marker
              key={index}
              position={[
                hotspot.cell_lat,
                hotspot.cell_lon,
              ]}
            >
              <Popup>
                <HotspotPopup
                  hotspot={
                    hotspot
                  }
                />
              </Popup>
            </Marker>
          );
        }
      )}
    </MapContainer>
  );
}
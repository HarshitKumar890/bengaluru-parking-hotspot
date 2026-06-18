import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import HotspotPopup from "./HotspotPopup";

import { MAP_CONFIG } from "../../utils/mapHelpers.js";

export default function HotspotMap({
  hotspots,
}) {
  return (
    <MapContainer
      center={[
        MAP_CONFIG.center[0],
        MAP_CONFIG.center[1]
      ]}
      zoom={MAP_CONFIG.zoom}
      style={{
        height: "700px",
        width: "100%",
      }}
    >
      <TileLayer
        attribution={MAP_CONFIG.attribution}
        url={MAP_CONFIG.tileLayerUrl}
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
export const MAP_CONFIG = {
  center: [
    Number(import.meta.env.VITE_MAP_LAT),
    Number(import.meta.env.VITE_MAP_LNG),
  ],
  zoom: Number(import.meta.env.VITE_MAP_ZOOM),
  tileLayerUrl: import.meta.env.VITE_TILE_LAYER_URL,
  attribution: import.meta.env.VITE_TILE_LAYER_ATTRIBUTION,
};
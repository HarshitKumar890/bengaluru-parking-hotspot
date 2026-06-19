import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useForecast() {
  const [forecasts, setForecasts] = useState([]);
  const [metadata, setMetadata] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchForecast = async () => {
    try {
      setError("");

      const response = await API.get(
        "/forecast?limit=50"
      );

      setForecasts(
        response.data?.data || []
      );

      setMetadata({
        model_loaded:
          response.data?.model_loaded,
        snapshot_note:
          response.data?.snapshot_note,
        total: response.data?.total,
        returned:
          response.data?.returned,
      });
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load forecast data"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchForecast();
  }, []);

  return {
    forecasts,
    metadata,
    loading,
    error,
    fetchForecast,
  };
}
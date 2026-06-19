import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useHotspots() {
  const [hotspots, setHotspots] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const fetchHotspots = async () => {
    try {
      setError("");

      const response = await API.get(
        "/hotspots?limit=1000"
      );

      setHotspots(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);

      setError(
        "Failed to load hotspot map"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHotspots();
  }, []);

  return {
    hotspots,
    loading,
    error,
    fetchHotspots,
  };
}
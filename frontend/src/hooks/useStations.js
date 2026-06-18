import { useEffect, useState } from "react";
import API from "../api/axios";

export default function useStations() {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchStations = async () => {
      try {
        const response = await API.get("/stations?limit=10");

        setStations(response.data.data || []);
      } catch (err) {
        console.error(err);
        setError("Failed to load station analytics");
      } finally {
        setLoading(false);
      }
    };

    fetchStations();
  }, []);

  return {
    stations,
    loading,
    error,
  };
}
import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useRiskZones() {
  const [riskZones, setRiskZones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchRiskZones = async () => {
    try {
      setError("");

      const response = await API.get(
        "/risk-zones?limit=100"
      );

      setRiskZones(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load risk zones"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRiskZones();
  }, []);

  return {
    riskZones,
    loading,
    error,
    fetchRiskZones,
  };
}
import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useStability() {
  const [stabilityData, setStabilityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchStability = async () => {
    try {
      setError("");

      const response = await API.get(
        "/stability?limit=200"
      );

      setStabilityData(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load stability analytics"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStability();
  }, []);

  return {
    stabilityData,
    loading,
    error,
    fetchStability,
  };
}
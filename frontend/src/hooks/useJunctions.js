import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useJunctions() {
  const [junctions, setJunctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchJunctions = async () => {
    try {
      setError("");

      const response = await API.get(
        "/junctions?limit=20"
      );

      setJunctions(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load junction analytics"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJunctions();
  }, []);

  return {
    junctions,
    loading,
    error,
    fetchJunctions,
  };
}
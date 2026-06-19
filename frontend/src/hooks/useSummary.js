import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchSummary = async () => {
    try {
      setError("");

      const response = await API.get("/summary");

      setSummary(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load dashboard summary");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  return {
    summary,
    loading,
    error,
    fetchSummary,
  };
}
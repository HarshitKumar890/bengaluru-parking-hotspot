import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useHealth() {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    try {
      const response = await API.get("/health");
      setHealth(response.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return {
    health,
    loading,
    fetchHealth,
  };
}
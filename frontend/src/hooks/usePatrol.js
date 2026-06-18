import { useEffect, useState } from "react";
import API from "../api/axios";

export default function usePatrol() {
  const [patrols, setPatrols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchPatrols = async () => {
    try {
      setError("");

      const response = await API.get(
        "/patrol-recommendations?limit=20"
      );

      setPatrols(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load patrol recommendations"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatrols();
  }, []);

  return {
    patrols,
    loading,
    error,
    fetchPatrols,
  };
}
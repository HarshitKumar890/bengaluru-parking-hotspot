import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useFeatureImportance() {
  const [features, setFeatures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchFeatures = async () => {
    try {
      setError("");

      const response = await API.get(
        "/feature-importance?limit=30"
      );

      setFeatures(
        response.data?.data || []
      );
    } catch (err) {
      console.error(err);
      setError(
        "Failed to load feature importance"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeatures();
  }, []);

  return {
    features,
    loading,
    error,
    fetchFeatures,
  };
}
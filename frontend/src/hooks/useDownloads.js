import { useEffect, useState } from "react";
import API from "../api/axios.js";

export default function useDownloads() {
  const [datasets, setDatasets] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const fetchDatasets = async () => {
  try {
    setError("");

    const response = await API.get(
      "/download"
    );

    setDatasets(
      response.data?.available_datasets || []
    );
  } catch (err) {
    console.error(err);

    setError(
      "Failed to load downloadable datasets"
    );
  } finally {
    setLoading(false);
  }
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  return {
    datasets,
    loading,
    error,
    fetchDatasets,
  };
}
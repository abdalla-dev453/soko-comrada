import { useCallback, useEffect, useState } from "react";

import { fetchGigs } from "../api/gigs";

const initialFilters = { campus: "", category: "", urgent: "", type: "" };

export function useGigs(initial = {}) {
  const [filters, setFilters] = useState({ ...initialFilters, ...initial });
  const [page, setPage] = useState(1);
  const [gigs, setGigs] = useState([]);
  const [meta, setMeta] = useState({ total: 0, totalPages: 1 });
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setStatus("loading");
    setError(null);
    try {
      const data = await fetchGigs(filters, page);
      setGigs(data.gigs);
      setMeta({ total: data.total, totalPages: data.total_pages });
      setStatus("success");
    } catch (err) {
      setError(err);
      setStatus("error");
    }
  }, [filters, page]);

  useEffect(() => {
    load();
  }, [load]);

  const updateFilters = useCallback((patch) => {
    setPage(1);
    setFilters((current) => ({ ...current, ...patch }));
  }, []);

  const resetFilters = useCallback(() => {
    setPage(1);
    setFilters(initialFilters);
  }, []);

  return {
    gigs,
    filters,
    updateFilters,
    resetFilters,
    page,
    setPage,
    totalPages: meta.totalPages,
    total: meta.total,
    isLoading: status === "loading",
    isError: status === "error",
    isEmpty: status === "success" && gigs.length === 0,
    error,
    reload: load,
  };
}
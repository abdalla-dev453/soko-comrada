const STORAGE_KEY = "comradeplug_saved_searches";
const ALERTS_KEY = "comradeplug_alert_preferences";

const defaultAlertPreferences = {
  matchingGigs: true,
  applicationUpdates: true,
};

export function getSavedSearches() {
  if (typeof window === "undefined") return [];

  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function upsertSavedSearch(search) {
  if (typeof window === "undefined") return null;

  const cleaned = {
    id: search.id || `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    name: String(search.name || "Saved search").trim(),
    filters: search.filters || {},
    createdAt: search.createdAt || new Date().toISOString(),
  };

  if (!cleaned.name) return null;

  const searches = getSavedSearches();
  const existingIndex = searches.findIndex(
    (item) => item.name.trim().toLowerCase() === cleaned.name.toLowerCase()
  );

  const next = [...searches];
  if (existingIndex >= 0) {
    next[existingIndex] = { ...next[existingIndex], ...cleaned, createdAt: next[existingIndex].createdAt };
  } else {
    next.unshift(cleaned);
  }

  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next[existingIndex >= 0 ? existingIndex : 0];
}

export function removeSavedSearch(searchId) {
  if (typeof window === "undefined") return [];

  const next = getSavedSearches().filter((item) => item.id !== searchId);
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  return next;
}

export function getAlertPreferences() {
  if (typeof window === "undefined") return defaultAlertPreferences;

  try {
    const raw = window.localStorage.getItem(ALERTS_KEY);
    const parsed = raw ? JSON.parse(raw) : {};
    return { ...defaultAlertPreferences, ...parsed };
  } catch {
    return defaultAlertPreferences;
  }
}

export function setAlertPreferences(nextPreferences) {
  if (typeof window === "undefined") return defaultAlertPreferences;

  const value = { ...defaultAlertPreferences, ...nextPreferences };
  window.localStorage.setItem(ALERTS_KEY, JSON.stringify(value));
  return value;
}

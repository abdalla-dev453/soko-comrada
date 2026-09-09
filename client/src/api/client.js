/**
 * Thin fetch wrapper for the Soko Comrada API.
 *
 * Responsibilities:
 *  - attach the JWT access token to every request
 *  - on a 401, try exactly once to refresh the access token and
 *    replay the original request (silent re-auth)
 *  - normalize error responses into a single ApiError shape so
 *    callers never have to branch on fetch's own error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "/api";

const TOKEN_STORAGE_KEY = "soko_comrada_tokens";

export class ApiError extends Error {
  constructor(message, { status, code, details } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function getStoredTokens() {
  try {
    const raw = localStorage.getItem(TOKEN_STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function storeTokens(tokens) {
  if (!tokens) {
    localStorage.removeItem(TOKEN_STORAGE_KEY);
    return;
  }
  localStorage.setItem(TOKEN_STORAGE_KEY, JSON.stringify(tokens));
}

async function refreshAccessToken() {
  const tokens = getStoredTokens();
  if (!tokens?.refresh_token) return null;

  const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
    method: "POST",
    headers: { Authorization: `Bearer ${tokens.refresh_token}` },
  });
  if (!res.ok) {
    storeTokens(null);
    return null;
  }
  const data = await res.json();
  const next = { ...tokens, access_token: data.access_token };
  storeTokens(next);
  return next;
}

async function parseErrorBody(res) {
  try {
    const body = await res.json();
    return {
      message:
        typeof body.message === "string"
          ? body.message
          : "Something went wrong. Please try again.",
      code: body.error,
      details: typeof body.message === "object" ? body.message : undefined,
    };
  } catch {
    return { message: "Something went wrong. Please try again." };
  }
}

/**
 * @param {string} path - e.g. "/gigs" (relative to API_BASE_URL)
 * @param {RequestInit & { skipAuth?: boolean }} [options]
 */
export async function apiRequest(path, options = {}) {
  const { skipAuth = false, headers, body, ...rest } = options;

  const doFetch = async () => {
    const tokens = getStoredTokens();
    const finalHeaders = { ...headers };
    const isJsonBody = body && typeof body === "object" && !(body instanceof FormData);

    if (isJsonBody) finalHeaders["Content-Type"] = "application/json";
    if (!skipAuth && tokens?.access_token) {
      finalHeaders["Authorization"] = `Bearer ${tokens.access_token}`;
    }

    return fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      headers: finalHeaders,
      body: isJsonBody ? JSON.stringify(body) : body,
    });
  };

  let res = await doFetch();

  if (res.status === 401 && !skipAuth) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      res = await doFetch();
    }
  }

  if (!res.ok) {
    const { message, code, details } = await parseErrorBody(res);
    throw new ApiError(message, { status: res.status, code, details });
  }

  if (res.status === 204) return null;
  return res.json();
}

export const apiClient = {
  get: (path, options) => apiRequest(path, { ...options, method: "GET" }),
  post: (path, body, options) => apiRequest(path, { ...options, method: "POST", body }),
  patch: (path, body, options) => apiRequest(path, { ...options, method: "PATCH", body }),
  delete: (path, options) => apiRequest(path, { ...options, method: "DELETE" }),
};
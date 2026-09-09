import { apiClient, storeTokens } from "./client";

export async function register(payload) {
  const data = await apiClient.post("/auth/register", payload, { skipAuth: true });
  storeTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
  return data.user;
}

export async function login(email, password) {
  const data = await apiClient.post(
    "/auth/login",
    { email, password },
    { skipAuth: true }
  );
  storeTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
  return data.user;
}

export function logout() {
  storeTokens(null);
}

export async function fetchMe() {
  const data = await apiClient.get("/auth/me");
  return data.user;
}

export async function fetchNotifications() {
  const data = await apiClient.get("/auth/notifications");
  return data.notifications;
}

export async function updateProfile(patch) {
  const data = await apiClient.patch("/auth/me", patch);
  return data.user;
}
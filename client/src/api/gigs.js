import { apiClient } from "./client";

export async function fetchGigs(filters = {}, page = 1) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      params.set(key, value);
    }
  });
  params.set("page", String(page));
  return apiClient.get(`/gigs?${params.toString()}`, { skipAuth: true });
}

export async function fetchGig(gigId) {
  const data = await apiClient.get(`/gigs/${gigId}`, { skipAuth: true });
  return data.gig;
}

export async function createGig(payload) {
  const data = await apiClient.post("/gigs", payload);
  return data.gig;
}

export async function applyToGig(gigId, proposalText) {
  const data = await apiClient.post(`/gigs/${gigId}/applications`, {
    proposal_text: proposalText,
  });
  return data.application;
}

export async function fetchGigApplications(gigId) {
  const data = await apiClient.get(`/gigs/${gigId}/applications`);
  return data.applications;
}

export async function completeGig(gigId) {
  return apiClient.post(`/gigs/${gigId}/complete`);
}

export async function decideApplication(applicationId, status) {
  return apiClient.patch(`/applications/${applicationId}`, { status });
}

export async function fetchMyGigs() {
  const data = await apiClient.get("/gigs/mine");
  return data.gigs;
}

export async function fetchMyApplications() {
  const data = await apiClient.get("/applications/mine");
  return data.applications;
}

export async function submitReview({ gigId, revieweeId, rating, comment }) {
  const data = await apiClient.post("/reviews", {
    gig_id: gigId,
    reviewee_id: revieweeId,
    rating,
    comment,
  });
  return data.review;
}

export async function fetchReviewsForUser(userId) {
  return apiClient.get(`/reviews/user/${userId}`, { skipAuth: true });
}

export async function submitReport({ reason, reportedGigId, reportedUserId }) {
  const data = await apiClient.post("/reports", {
    reason,
    reported_gig_id: reportedGigId,
    reported_user_id: reportedUserId,
  });
  return data.report;
}
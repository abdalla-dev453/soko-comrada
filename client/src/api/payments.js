import { apiClient } from "./client";

export async function submitPayment({ mpesaCode, purpose, gigId }) {
  const data = await apiClient.post("/payments/verify", {
    mpesa_code: mpesaCode,
    purpose,
    gig_id: gigId,
  });
  return data.payment;
}

export async function fetchMyPayments() {
  const data = await apiClient.get("/payments/mine");
  return data.payments;
}

// --- Admin-only ---

export async function fetchPendingPayments() {
  const data = await apiClient.get("/admin/payments/pending");
  return data.payments;
}

export async function decidePayment(paymentId, approve) {
  const data = await apiClient.post(`/admin/payments/${paymentId}/decision`, { approve });
  return data.payment;
}

export async function fetchReports(status) {
  const query = status ? `?status=${status}` : "";
  const data = await apiClient.get(`/admin/reports${query}`);
  return data.reports;
}

export async function resolveReport(reportId, status) {
  const data = await apiClient.patch(`/admin/reports/${reportId}`, { status });
  return data.report;
}
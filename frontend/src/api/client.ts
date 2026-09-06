import type { AnalysisEnvelope, AnalysisRunResponse, ApiError, HealthResponse, WebsiteCreateRequest, WebsiteEnvelope, WebsiteResponse } from "./contracts";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000/api/v1";

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("The Trellis API is unavailable.");
  }
  return response.json() as Promise<HealthResponse>;
}

export class ApiRequestError extends Error {
  constructor(public readonly code: string, message: string) {
    super(message);
  }
}

export async function createWebsite(payload: WebsiteCreateRequest, accessToken: string): Promise<WebsiteResponse> {
  const response = await fetch(`${API_BASE_URL}/websites`, {
    method: "POST",
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as ApiError | null;
    throw new ApiRequestError(error?.error ?? "request_failed", error?.message ?? "Trellis could not create the website workspace.");
  }
  return ((await response.json()) as WebsiteEnvelope).data;
}

async function analysisRequest(path: string, accessToken: string, method = "GET"): Promise<AnalysisRunResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, { method, headers: { Authorization: `Bearer ${accessToken}` } });
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as ApiError | null;
    throw new ApiRequestError(error?.error ?? "request_failed", error?.message ?? "Trellis could not update this analysis.");
  }
  return ((await response.json()) as AnalysisEnvelope).data;
}

export function startAnalysis(websiteId: number, accessToken: string) {
  return analysisRequest(`/websites/${websiteId}/analysis-runs`, accessToken, "POST");
}

export function getAnalysis(analysisId: number, accessToken: string) {
  return analysisRequest(`/analysis-runs/${analysisId}`, accessToken);
}

export function retryAnalysis(analysisId: number, accessToken: string) {
  return analysisRequest(`/analysis-runs/${analysisId}/retry`, accessToken, "POST");
}

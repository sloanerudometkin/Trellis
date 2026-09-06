import type { AnalysisEnvelope, AnalysisRunResponse, ApiError, DismissReason, HealthResponse, OrganizerEnvelope, OrganizerItemEnvelope, OrganizerItemResponse, OrganizerStage, SuggestionEnvelope, SuggestionResponse, WebsiteCreateRequest, WebsiteEnvelope, WebsiteResponse } from "./contracts";

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

async function authenticatedRequest<T>(path: string, accessToken: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: { Authorization: `Bearer ${accessToken}`, "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const error = (await response.json().catch(() => null)) as ApiError | null;
    throw new ApiRequestError(error?.error ?? "request_failed", error?.message ?? "Trellis could not update your plan.");
  }
  return response.json() as Promise<T>;
}

export async function decideSuggestion(suggestionId: number, status: "accepted" | "dismissed", accessToken: string, dismissReason?: DismissReason): Promise<SuggestionResponse> {
  const envelope = await authenticatedRequest<SuggestionEnvelope>(`/suggestions/${suggestionId}/decision`, accessToken, {
    method: "PATCH", body: JSON.stringify({ status, ...(dismissReason ? { dismiss_reason: dismissReason } : {}) }),
  });
  return envelope.data;
}

export async function updateSuggestionStage(suggestionId: number, stage: OrganizerStage, accessToken: string): Promise<SuggestionResponse> {
  const envelope = await authenticatedRequest<SuggestionEnvelope>(`/suggestions/${suggestionId}/stage`, accessToken, { method: "PATCH", body: JSON.stringify({ stage }) });
  return envelope.data;
}

export async function getOrganizerItems(websiteId: number, accessToken: string): Promise<OrganizerItemResponse[]> {
  const envelope = await authenticatedRequest<OrganizerEnvelope>(`/websites/${websiteId}/organizer-items`, accessToken);
  return envelope.data;
}

export async function updateOrganizerItem(itemId: number, stage: OrganizerStage, accessToken: string): Promise<OrganizerItemResponse> {
  const envelope = await authenticatedRequest<OrganizerItemEnvelope>(`/organizer-items/${itemId}`, accessToken, { method: "PATCH", body: JSON.stringify({ stage }) });
  return envelope.data;
}

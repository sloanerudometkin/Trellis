import type { HealthResponse } from "./contracts";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5000/api/v1";

export async function getApiHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error("The Trellis API is unavailable.");
  }
  return response.json() as Promise<HealthResponse>;
}

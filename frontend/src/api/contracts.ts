export interface ApiError {
  error: string;
  message: string;
}

export interface HealthResponse {
  status: "ok";
  service: "trellis-api";
}

export interface WebsiteCreateRequest {
  url: string;
  business_name: string;
  business_context?: string;
}

export interface WebsiteEnvelope {
  data: WebsiteResponse;
}

export interface WebsiteResponse extends WebsiteCreateRequest {
  id: number;
  google_ads_connected: boolean;
  ga4_connected: boolean;
}

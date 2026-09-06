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

export type AnalysisStatus = "queued" | "scraping" | "analyzing" | "generating" | "completed" | "failed";

export interface KeywordResponse {
  phrase: string;
  frequency: number;
  tfidf_score: number;
}

export interface AnalysisRunResponse {
  id: number;
  website_id: number;
  status: AnalysisStatus;
  last_completed_stage: string | null;
  pages_scanned_count: number;
  error_message: string | null;
  started_at: string;
  completed_at: string | null;
  keywords: KeywordResponse[];
}

export interface AnalysisEnvelope {
  data: AnalysisRunResponse;
}

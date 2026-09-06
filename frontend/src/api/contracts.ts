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

export interface SuggestionKeywordResponse {
  phrase: string;
  recommended_usage_count: number;
}

export interface SuggestionResponse {
  id: number;
  category: "aeo" | "seo_content" | "sem";
  title: string;
  description: string;
  starter_outline: string[] | null;
  rationale: string;
  priority: "low" | "medium" | "high";
  status: "pending" | "accepted" | "dismissed";
  stage: string;
  affected_page_url: string | null;
  target_keywords: SuggestionKeywordResponse[];
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
  suggestions: SuggestionResponse[];
}

export interface AnalysisEnvelope {
  data: AnalysisRunResponse;
}

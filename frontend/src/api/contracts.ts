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
  recommended_usage_count: number | null;
}

export interface SuggestionResponse {
  id: number;
  category: "aeo" | "seo_content" | "sem";
  title: string;
  description: string;
  starter_outline?: string[] | null;
  rationale: string;
  priority: "low" | "medium" | "high";
  status: "pending" | "accepted" | "dismissed";
  dismiss_reason: DismissReason | null;
  stage: string;
  organizer_item_id: number | null;
  affected_page_url: string | null;
  target_keywords: SuggestionKeywordResponse[];
  cost_tier?: "low" | "medium" | "high" | null;
  cost_tier_disclosure?: string | null;
  sem_keyword?: string | null;
  ad_group_label?: string | null;
  ad_copy_angle?: string | null;
  landing_page_match?: string | null;
  targeting_notes?: string | null;
  negative_keywords?: string[] | null;
  cheaper_alternative_to_id?: number | null;
  campaign_boundary?: string | null;
}

export type DismissReason = "not_relevant" | "too_much_work" | "already_doing_this" | "other";
export type OrganizerStage = "backlog" | "in_production" | "in_review" | "published";

export interface OrganizerItemResponse {
  id: number;
  website_id: number;
  suggestion_id: number | null;
  item_type: "aeo" | "seo_content" | "sem";
  title: string;
  stage: OrganizerStage;
  published_at: string | null;
}

export interface OrganizerEnvelope { data: OrganizerItemResponse[]; }
export interface OrganizerItemEnvelope { data: OrganizerItemResponse; }
export interface SuggestionEnvelope { data: SuggestionResponse; }

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
  technical_audit: TechnicalAuditResponse;
  sem_summary: SemSummaryResponse;
}

export interface SemSummaryResponse {
  candidate_count: number;
  accepted_count: number;
  cost_tier_counts: Record<"low" | "medium" | "high", number>;
  estimated_cost_range: string | null;
  cost_tier_disclosure: string;
  campaign_boundary: string;
}

export interface TechnicalFindingResponse {
  id: number;
  finding_type: string;
  severity: "low" | "medium" | "high" | "critical";
  explanation: string;
  affected_page_url: string | null;
  related_page_url: string | null;
  resolution_status: "open" | "resolved";
}

export interface TechnicalAuditResponse {
  summary: string;
  findings: TechnicalFindingResponse[];
}

export interface AnalysisEnvelope {
  data: AnalysisRunResponse;
}

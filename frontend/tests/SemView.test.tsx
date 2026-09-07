import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SemView } from "../src/SemView";
import type { AnalysisRunResponse } from "../src/api/contracts";

const disclosure = "Heuristic estimate based on keyword shape and intent—not live Google Ads bid data.";
const campaignBoundary = "Planning only: Trellis cannot create, launch, manage, bid on, or spend money on advertising campaigns.";
const analysis: AnalysisRunResponse = {
  id: 1, website_id: 1, status: "completed", last_completed_stage: "generating", pages_scanned_count: 2,
  error_message: null, started_at: "2026-09-07T12:00:00Z", completed_at: "2026-09-07T12:01:00Z", keywords: [],
  technical_audit: { summary: "No issues.", findings: [] },
  sem_summary: { candidate_count: 2, accepted_count: 0, cost_tier_counts: { low: 1, medium: 1, high: 0 }, estimated_cost_range: "Low–Medium heuristic Cost Tier", cost_tier_disclosure: disclosure, campaign_boundary: campaignBoundary },
  suggestions: [
    { id: 4, category: "sem", title: "Test garden workshops", description: "Test a focused keyword group.", rationale: "Tight theming supports Quality Score and helps control CPC.", priority: "medium", status: "pending", dismiss_reason: null, stage: "suggested", organizer_item_id: null, affected_page_url: "https://example.com/", target_keywords: [], cost_tier: "medium", cost_tier_disclosure: disclosure, sem_keyword: "garden workshops", ad_group_label: "Garden Workshops intent", ad_copy_angle: "Lead with practical workshops.", landing_page_match: "https://example.com/", targeting_notes: "Use the Google Search network within 15 miles.", negative_keywords: ["jobs", "free"], cheaper_alternative_to_id: null, campaign_boundary: campaignBoundary },
    { id: 5, category: "sem", title: "Try garden workshops near me", description: "Test the longer phrase.", rationale: "The longer phrase has a lower heuristic tier.", priority: "high", status: "pending", dismiss_reason: null, stage: "suggested", organizer_item_id: null, affected_page_url: "https://example.com/", target_keywords: [], cost_tier: "low", cost_tier_disclosure: disclosure, sem_keyword: null, ad_group_label: "Garden Workshops intent", ad_copy_angle: "Lead with practical workshops.", landing_page_match: "https://example.com/", targeting_notes: "Use the Google Search network within 15 miles.", negative_keywords: ["jobs", "free"], cheaper_alternative_to_id: 4, campaign_boundary: campaignBoundary },
  ],
};

describe("MVP-011 SEM view", () => {
  it("shows summary, ad groups, alternatives, targeting, landing pages, and negatives", () => {
    render(<SemView analysis={analysis} onDecision={vi.fn()} onStageChange={vi.fn()} />);
    expect(screen.getByRole("region", { name: "SEM summary" })).toHaveTextContent("2 keyword candidates · 0 accepted");
    expect(screen.getByRole("region", { name: /Ad group details for Test garden workshops/ })).toHaveTextContent("Garden Workshops intent");
    expect(screen.getByText("Cheaper alternative")).toBeInTheDocument();
    expect(screen.getAllByText("jobs")).toHaveLength(2);
    expect(screen.getAllByText(/Google Search network/)).toHaveLength(2);
  });

  it("labels every displayed Cost Tier as a heuristic estimate", () => {
    render(<SemView analysis={analysis} onDecision={vi.fn()} onStageChange={vi.fn()} />);
    for (const card of screen.getAllByTestId("recommendation-card")) {
      expect(card).toHaveTextContent(/Cost Tier: .*heuristic estimate/i);
      expect(card).toHaveTextContent("not live Google Ads bid data");
    }
    expect(screen.getByRole("region", { name: "SEM summary" })).toHaveTextContent("heuristic Cost Tier");
    expect(screen.getByRole("region", { name: "SEM summary" })).toHaveTextContent("not live Google Ads bid data");
  });

  it("states the planning boundary and exposes no campaign or spending action", () => {
    render(<SemView analysis={analysis} onDecision={vi.fn()} onStageChange={vi.fn()} />);
    expect(screen.getByText(campaignBoundary)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /launch|campaign|spend|bid/i })).not.toBeInTheDocument();
  });
});

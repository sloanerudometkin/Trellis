import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RecommendationView } from "../src/RecommendationView";
import type { AnalysisRunResponse } from "../src/api/contracts";

const completed: AnalysisRunResponse = {
  id: 31, website_id: 12, status: "completed", last_completed_stage: "generating",
  pages_scanned_count: 2, error_message: null, started_at: "2026-09-06T12:00:00Z",
  completed_at: "2026-09-06T12:01:00Z", keywords: [],
  technical_audit: { summary: "No problems found.", findings: [] },
  suggestions: [
    { id: 1, category: "aeo", title: "Add a direct answer", description: "Answer the visitor’s main question below the heading.", rationale: "This helps answer engines understand the page.", priority: "high", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: "https://example.com/", starter_outline: null, target_keywords: [] },
    { id: 2, category: "seo_content", title: "Publish a planting guide", description: "Create a useful guide for local gardeners.", rationale: "The website does not currently answer this search need.", priority: "medium", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: null, starter_outline: ["Choose plants", "Prepare the bed"], target_keywords: [{ phrase: "community garden", recommended_usage_count: 4 }] },
  ],
};

describe("MVP-008 recommendation components", () => {
  it("shows AEO recommendation content, rationale, priority, and stage", () => {
    render(<RecommendationView analysis={completed} kind="aeo" />);
    expect(screen.getByText("Add a direct answer")).toBeInTheDocument();
    expect(screen.getByText("This helps answer engines understand the page.")).toBeInTheDocument();
    expect(screen.getByText("high priority")).toBeInTheDocument();
    expect(screen.getByText("Suggested")).toBeInTheDocument();
  });

  it("shows an SEO/content outline, target keyword, and usage count", () => {
    render(<RecommendationView analysis={completed} kind="seo_content" />);
    expect(screen.getByRole("region", { name: "Starter outline" })).toHaveTextContent("Choose plants");
    expect(screen.getByRole("region", { name: "Target keywords" })).toHaveTextContent("community garden");
    expect(screen.getByRole("region", { name: "Target keywords" })).toHaveTextContent("Use about 4×");
  });

  it.each([
    [null, "Run your first website analysis from Overview."],
    [{ ...completed, status: "generating" }, "Your analysis is still in progress."],
    [{ ...completed, suggestions: [] }, "No AEO actions were found"],
    [{ ...completed, status: "failed", error_message: "The provider was unavailable." }, "The provider was unavailable."],
  ] as const)("renders the incomplete, loading, empty, or failed state", (analysis, expected) => {
    render(<RecommendationView analysis={analysis as AnalysisRunResponse | null} kind="aeo" />);
    expect(screen.getByText(new RegExp(expected))).toBeInTheDocument();
  });

  it("shows a request failure instead of stale content", () => {
    render(<RecommendationView analysis={completed} kind="aeo" requestError="We lost contact with the analysis. Please try again." />);
    expect(screen.getByRole("alert")).toHaveTextContent("We lost contact");
  });

  it("accepts a pending recommendation", async () => {
    const onDecision = vi.fn().mockResolvedValue(undefined);
    render(<RecommendationView analysis={completed} kind="aeo" onDecision={onDecision} />);
    fireEvent.click(screen.getByRole("button", { name: "Accept" }));
    await waitFor(() => expect(onDecision).toHaveBeenCalledWith(completed.suggestions[0], "accepted"));
  });

  it("offers one-tap dismiss reasons", async () => {
    const onDecision = vi.fn().mockResolvedValue(undefined);
    render(<RecommendationView analysis={completed} kind="aeo" onDecision={onDecision} />);
    fireEvent.click(screen.getByRole("button", { name: "Dismiss" }));
    fireEvent.click(screen.getByRole("button", { name: "Not relevant" }));
    await waitFor(() => expect(onDecision).toHaveBeenCalledWith(completed.suggestions[0], "dismissed", "not_relevant"));
  });

  it("changes an accepted recommendation through its canonical Organizer stage", async () => {
    const onStageChange = vi.fn().mockResolvedValue(undefined);
    const accepted = { ...completed, suggestions: [{ ...completed.suggestions[0], status: "accepted" as const, stage: "backlog", organizer_item_id: 9 }] };
    render(<RecommendationView analysis={accepted} kind="aeo" onStageChange={onStageChange} />);
    fireEvent.change(screen.getByLabelText("Stage for Add a direct answer"), { target: { value: "in_review" } });
    await waitFor(() => expect(onStageChange).toHaveBeenCalledWith(accepted.suggestions[0], "in_review"));
  });
});

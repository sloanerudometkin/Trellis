import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "../src/App";

const website = { id: 7, url: "https://example.com", business_name: "Example Studio", business_context: null, google_ads_connected: false, ga4_connected: false };
const suggestion = (id: number, category: "aeo" | "seo_content" | "sem", title: string) => ({ id, category, title, description: `${title} description`, rationale: `${title} rationale`, priority: "high", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: "https://example.com", starter_outline: category === "seo_content" ? ["Start here"] : null, target_keywords: category === "seo_content" ? [{ phrase: "community garden", recommended_usage_count: 3 }] : [], ...(category === "sem" ? { cost_tier: "low", cost_tier_disclosure: "Heuristic estimate", sem_keyword: "garden help", ad_group_label: "Garden", ad_copy_angle: "Grow", landing_page_match: "https://example.com", targeting_notes: "Search", negative_keywords: ["free"], cheaper_alternative_to_id: null, campaign_boundary: "Planning only" } : {}) });
const completed = (partial = false) => ({ id: 20, website_id: 7, status: "completed", last_completed_stage: "generating", pages_scanned_count: 3, error_message: partial ? "Analysis completed with 1 page request failure(s)." : null, started_at: "2026-09-07T12:00:00Z", completed_at: "2026-09-07T12:01:00Z", keywords: [{ phrase: "community garden", frequency: 5, tfidf_score: .8 }], suggestions: [suggestion(1, "aeo", "Add direct answers"), suggestion(2, "seo_content", "Publish a guide"), suggestion(3, "sem", "Plan an ad group")], technical_audit: { summary: "Fix the page title first.", findings: [] }, sem_summary: { candidate_count: 1, accepted_count: 0, cost_tier_counts: { low: 1, medium: 0, high: 0 }, estimated_cost_range: "Low", cost_tier_disclosure: "Heuristic estimate", campaign_boundary: "Planning only" }, health_score: 64, health_score_delta: 9, health_score_history: [{ analysis_id: 19, score: 55, completed_at: "2026-08-07T12:00:00Z" }, { analysis_id: 20, score: 64, completed_at: "2026-09-07T12:01:00Z" }], health_score_disclosure: "Organic only; SEM excluded." });
const report = { id: 4, website_id: 7, analysis_run_id: 20, generated_at: "2026-09-07T12:01:00Z", summary_text: "Health Score up 9 points.", health_score: 64, health_score_delta: 9, aeo_completion_pct: 25, aeo_completion_delta: 10, technical_findings_resolved: 1, technical_findings_open: 0, content_published_count: 1, top_keywords: ["community garden"], sem_accepted_count: 2, sem_cost_tier_breakdown: { low: 2, medium: 0, high: 0 }, ad_groups_defined_count: 1, organizer_stage_counts: { backlog: 1, in_production: 1, in_review: 0, published: 1 }, disclosure: "Saved snapshot." };
const organizer = [{ id: 10, website_id: 7, suggestion_id: 2, item_type: "seo_content", title: "Publish a guide", stage: "backlog", published_at: null }];

function start(fetchMock: ReturnType<typeof vi.fn>) {
  vi.stubGlobal("fetch", fetchMock); render(<App />);
  fireEvent.change(screen.getByLabelText("Website URL"), { target: { value: "example.com" } }); fireEvent.change(screen.getByLabelText("Business or organization name"), { target: { value: "Example Studio" } }); fireEvent.click(screen.getByRole("button", { name: "Create workspace" }));
}
function router(analysis = completed()) { return vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => { const url = String(input); const method = init?.method ?? "GET"; let data: unknown = website; if (url.includes("analysis-runs") && method === "POST") data = analysis; else if (url.endsWith("/reports")) data = [report]; else if (url.endsWith("/organizer-items")) data = organizer; return { ok: true, json: async () => ({ data }) }; }); }

describe("MVP-014 integrated workspace", () => {
  beforeEach(() => localStorage.setItem("trellis_access_token", "token")); afterEach(() => { localStorage.clear(); vi.unstubAllGlobals(); });
  it("uses one website and AnalysisRun context across all six real-data views", async () => {
    start(router()); fireEvent.click(await screen.findByRole("button", { name: "Analyze website" }));
    const overview = await screen.findByRole("region", { name: "Overview summary" }); await waitFor(() => expect(overview).toHaveTextContent("25% complete"));
    const checks: [string, string][] = [["AEO", "Add direct answers"], ["SEO/Content", "Publish a guide"], ["SEM", "Plan an ad group"]];
    for (const [view, text] of checks) { fireEvent.click(screen.getByRole("button", { name: view })); expect(await screen.findByText(text)).toBeVisible(); expect(screen.getByText("Example Studio", { selector: "p.font-semibold" })).toBeVisible(); }
    fireEvent.click(screen.getByRole("button", { name: "Reports" })); expect(await screen.findByTestId("current-report-summary")).toHaveTextContent("Health Score up 9 points");
    fireEvent.click(screen.getByRole("button", { name: "Organizer" })); expect(await screen.findByTestId("organizer-item-10")).toHaveTextContent("Publish a guide");
  });
  it("supports arrow, Home, and End keyboard navigation and remains available at a narrow viewport", async () => {
    Object.defineProperty(window, "innerWidth", { configurable: true, value: 360 }); start(router());
    const overview = await screen.findByRole("button", { name: "Overview" }); overview.focus(); fireEvent.keyDown(overview, { key: "ArrowRight" }); expect(screen.getByRole("heading", { name: "AEO" })).toBeVisible();
    fireEvent.keyDown(screen.getByRole("button", { name: "AEO" }), { key: "End" }); expect(screen.getByRole("heading", { name: "Organizer" })).toBeVisible();
    fireEvent.keyDown(screen.getByRole("button", { name: "Organizer" }), { key: "Home" }); expect(screen.getByRole("heading", { name: "Overview" })).toBeVisible(); expect(screen.getByRole("navigation", { name: "Workspace views" })).toBeVisible();
  });
  it("shows empty, loading, partial, and failed/retry states", async () => {
    let resolveAnalysis!: (value: object) => void; const fetchMock = vi.fn((input: RequestInfo | URL, init?: RequestInit) => { const url = String(input); if (url.endsWith("/websites") && init?.method === "POST") return Promise.resolve({ ok: true, json: async () => ({ data: website }) }); if (url.includes("analysis-runs")) return new Promise((resolve) => { resolveAnalysis = resolve; }); return Promise.resolve({ ok: true, json: async () => ({ data: [] }) }); });
    start(fetchMock); fireEvent.click(await screen.findByRole("button", { name: "AEO" })); expect(screen.getByText(/Run your first website analysis/)).toBeVisible(); fireEvent.click(screen.getByRole("button", { name: "Overview" })); fireEvent.click(screen.getByRole("button", { name: "Analyze website" }));
    expect(screen.getByRole("button", { name: "Starting analysis…" })).toBeDisabled(); resolveAnalysis({ ok: true, json: async () => ({ data: completed(true) }) }); expect(await screen.findByText(/Partial analysis:/)).toBeVisible();
  });
  it("surfaces an unauthorized analysis response without exposing API internals", async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => String(input).endsWith("/websites") && init?.method === "POST" ? { ok: true, json: async () => ({ data: website }) } : { ok: false, json: async () => ({ error: "unauthorized", message: "token internals" }) });
    start(fetchMock); fireEvent.click(await screen.findByRole("button", { name: "Analyze website" })); await waitFor(() => expect(screen.getByRole("alert")).toHaveTextContent("session has expired")); expect(screen.queryByText("token internals")).not.toBeInTheDocument();
  });
});

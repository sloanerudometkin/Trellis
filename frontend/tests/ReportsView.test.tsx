import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { compareReports, getReports } from "../src/api/client";
import { ReportsView } from "../src/ReportsView";
import type { ReportResponse } from "../src/api/contracts";

vi.mock("../src/api/client", () => ({ getReports: vi.fn(), compareReports: vi.fn() }));

const report = (id: number, score: number): ReportResponse => ({
  id, website_id: 12, analysis_run_id: id + 20, generated_at: `2026-09-0${id}T12:00:00Z`, summary_text: `Health Score ${score}.`,
  health_score: score, health_score_delta: null, aeo_completion_pct: id * 10, aeo_completion_delta: null,
  technical_findings_resolved: id, technical_findings_open: 3 - id, content_published_count: id - 1, top_keywords: id === 1 ? ["garden"] : ["garden", "soil"],
  sem_accepted_count: id - 1, sem_cost_tier_breakdown: { low: id - 1, medium: 0, high: 0 }, ad_groups_defined_count: id,
  organizer_stage_counts: { backlog: id, in_production: 0, in_review: 0, published: id - 1 }, disclosure: "Saved snapshot: values do not change.",
});

describe("ReportsView", () => {
  beforeEach(() => { vi.mocked(getReports).mockResolvedValue([report(2, 70), report(1, 50)]); });
  it("groups all KPI families and reopens a historical report", async () => {
    render(<ReportsView websiteId={12} accessToken="token" />);
    expect(await screen.findByRole("region", { name: "Organic KPIs" })).toBeVisible();
    expect(screen.getByRole("region", { name: "Paid (heuristic) KPIs" })).toBeVisible();
    expect(screen.getByRole("region", { name: "Pipeline KPIs" })).toBeVisible();
    expect(screen.getByText(/Saved snapshot/)).toBeVisible();
    fireEvent.click(screen.getByRole("button", { name: /Sep 1, 2026/ }));
    expect(screen.getByTestId("current-report-summary")).toHaveTextContent("Health Score 50.");
  });
  it("defaults to latest versus previous and displays comparison deltas", async () => {
    vi.mocked(compareReports).mockResolvedValue({ before: report(1, 50), after: report(2, 70), deltas: { health_score: { absolute: 20, percentage: 40 }, top_keywords: { added: ["soil"], removed: [] } } });
    render(<ReportsView websiteId={12} accessToken="token" />);
    fireEvent.click(await screen.findByRole("button", { name: "Compare Reports" }));
    await waitFor(() => expect(compareReports).toHaveBeenCalledWith(12, 1, 2, "token"));
    expect(await screen.findByRole("region", { name: "Report comparison" })).toHaveTextContent("+20 (+40.0%)");
    expect(screen.getByText(/\+soil/)).toBeVisible();
  });
});

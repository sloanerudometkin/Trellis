import { expect, test } from "@playwright/test";

test("sign in → add website → analyze → view results", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("trellis_access_token", "e2e-token"));
  await page.route("**/api/v1/websites", async (route) => {
    expect(route.request().headers().authorization).toBe("Bearer e2e-token");
    await route.fulfill({
      status: 201,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          id: 12,
          url: "https://example.com",
          business_name: "Example Studio",
          business_context: "Independent design studio",
          google_ads_connected: false,
          ga4_connected: false,
        },
      }),
    });
  });
  let pollCount = 0;
  let accepted = false;
  let semAccepted = false;
  let organizerStage = "backlog";
  const analysis = (status: string) => ({
    id: 31, website_id: 12, status,
    last_completed_stage: status === "completed" ? "generating" : null,
    pages_scanned_count: status === "completed" ? 2 : 0,
    error_message: null,
    started_at: "2026-09-06T12:00:00Z",
    completed_at: status === "completed" ? "2026-09-06T12:01:00Z" : null,
    keywords: status === "completed" ? [{ phrase: "design studio", frequency: 4, tfidf_score: 0.9 }] : [],
    suggestions: status === "completed" ? [
      { id: 1, category: "aeo", title: "Answer the core design question", description: "Add a concise answer below the homepage heading.", rationale: "A direct answer helps visitors and answer engines understand the studio.", priority: "high", stage: "suggested", status: "pending", dismiss_reason: null, organizer_item_id: null, affected_page_url: "https://example.com/", starter_outline: null, target_keywords: [] },
      { id: 2, category: "seo_content", title: "Publish a design process guide", description: "Explain the studio’s process in a practical guide.", rationale: "This fills an information gap for prospective clients.", priority: "medium", stage: accepted ? organizerStage : "suggested", status: accepted ? "accepted" : "pending", dismiss_reason: null, organizer_item_id: accepted ? 22 : null, affected_page_url: null, starter_outline: ["Discovery", "Design", "Delivery"], target_keywords: [{ phrase: "design studio", recommended_usage_count: 4 }] },
      { id: 3, category: "sem", title: "Test the keyword: design studio", description: "Create a tightly matched search ad group.", rationale: "Tight keyword, ad, and landing-page alignment supports Quality Score and helps control CPC.", priority: "medium", stage: semAccepted ? "backlog" : "suggested", status: semAccepted ? "accepted" : "pending", dismiss_reason: null, organizer_item_id: semAccepted ? 23 : null, affected_page_url: "https://example.com/", starter_outline: null, target_keywords: [], cost_tier: "medium", cost_tier_disclosure: "Heuristic estimate based on keyword shape and intent—not live Google Ads bid data.", sem_keyword: "design studio", ad_group_label: "Design Studio intent", ad_copy_angle: "Lead with a clear design outcome.", landing_page_match: "https://example.com/", targeting_notes: "Use the Google Search network for high-intent searches.", negative_keywords: ["jobs", "free"], cheaper_alternative_to_id: null, campaign_boundary: "Planning only: Trellis cannot create, launch, manage, bid on, or spend money on advertising campaigns." },
    ] : [],
    technical_audit: status === "completed" ? { summary: "Fix first: Add descriptive image alt text so the design work is understandable.", findings: [{ id: 90, finding_type: "missing_image_alt", severity: "medium", explanation: "Add useful alt text to 1 image.", affected_page_url: "https://example.com/", related_page_url: null, resolution_status: "open" }] } : { summary: "", findings: [] },
    sem_summary: { candidate_count: 1, accepted_count: 0, cost_tier_counts: { low: 1, medium: 0, high: 0 }, estimated_cost_range: "Low–Low heuristic Cost Tier", cost_tier_disclosure: "Heuristic estimate based on keyword shape and intent—not live Google Ads bid data.", campaign_boundary: "Planning only: Trellis cannot create, launch, manage, bid on, or spend money on advertising campaigns." },
    health_score: status === "completed" ? 41 : null,
    health_score_delta: status === "completed" ? 6 : null,
    health_score_history: status === "completed" ? [{ analysis_id: 30, score: 35, completed_at: "2026-08-30T12:01:00Z" }, { analysis_id: 31, score: 41, completed_at: "2026-09-06T12:01:00Z" }] : [],
    health_score_disclosure: "Organic snapshot: 35% AEO completion, 35% resolved technical findings, and 30% published SEO/content work. SEM is excluded.",
  });
  await page.route("**/api/v1/websites/12/analysis-runs", async (route) => {
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ data: analysis("queued") }) });
  });
  await page.route("**/api/v1/analysis-runs/31", async (route) => {
    const statuses = ["scraping", "analyzing", "generating", "completed"];
    const status = statuses[Math.min(pollCount++, statuses.length - 1)];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: analysis(status) }) });
  });
  await page.route("**/api/v1/suggestions/2/decision", async (route) => {
    accepted = true;
    const suggestion = analysis("completed").suggestions[1];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: suggestion }) });
  });
  await page.route("**/api/v1/suggestions/3/decision", async (route) => {
    semAccepted = true;
    const suggestion = analysis("completed").suggestions[2];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: suggestion }) });
  });
  await page.route("**/api/v1/websites/12/organizer-items", async (route) => {
    const items = [];
    if (accepted) items.push({ id: 22, website_id: 12, suggestion_id: 2, item_type: "seo_content", title: "Publish a design process guide", stage: organizerStage, published_at: organizerStage === "published" ? "2026-09-06T12:05:00Z" : null });
    if (semAccepted) items.push({ id: 23, website_id: 12, suggestion_id: 3, item_type: "sem", title: "Test the keyword: design studio", stage: "backlog", published_at: null });
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: items }) });
  });
  await page.route("**/api/v1/organizer-items/22", async (route) => {
    organizerStage = (await route.request().postDataJSON()).stage;
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: { id: 22, website_id: 12, suggestion_id: 2, item_type: "seo_content", title: "Publish a design process guide", stage: organizerStage, published_at: "2026-09-06T12:05:00Z" } }) });
  });

  await page.goto("/");
  await page.getByLabel("Website URL").fill("example.com");
  await page.getByLabel("Business or organization name").fill("Example Studio");
  await page.getByLabel(/Business context/).fill("Independent design studio");
  const actionPlanTimerStartedAt = Date.now();
  await page.getByRole("button", { name: "Create workspace" }).click();

  await expect(page.getByRole("navigation", { name: "Workspace views" })).toBeVisible();
  await page.getByRole("button", { name: "Analyze website" }).click();
  await expect(page.getByRole("status")).toContainText("queued");
  await expect(page.getByTestId("analysis-results")).toContainText("2 pages analyzed", { timeout: 6000 });
  await expect(page.getByTestId("analysis-results")).toContainText("design studio ×4");
  await expect(page.getByRole("heading", { name: "41/100" })).toBeVisible();
  await expect(page.getByText("+6 points since prior scan")).toBeVisible();
  await expect(page.getByRole("img", { name: "Organic Health Score trend: 35, 41" })).toBeVisible();
  await expect(page.getByText(/SEM is excluded/)).toBeVisible();
  await page.getByRole("button", { name: "AEO" }).click();
  await expect(page.getByText("Answer the core design question")).toBeVisible();
  expect(Date.now() - actionPlanTimerStartedAt).toBeLessThan(5 * 60 * 1000);
  await page.getByRole("button", { name: "SEO/Content" }).click();
  await expect(page.getByRole("region", { name: "Starter outline" })).toContainText("Discovery");
  await expect(page.getByRole("region", { name: "Target keywords" })).toContainText("Use about 4×");
  await expect(page.getByRole("heading", { name: "Prioritized fix list" })).toBeVisible();
  await expect(page.getByTestId("fix-first-summary")).toContainText("Fix first");
  await expect(page.getByText("Image alt text", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Accept" }).click();
  await expect(page.getByLabel("Stage for Publish a design process guide")).toHaveValue("backlog");
  await page.getByRole("button", { name: "Organizer" }).click();
  await expect(page.getByRole("region", { name: "Backlog" })).toContainText("Publish a design process guide");
  await page.getByLabel("Stage for Publish a design process guide").selectOption("published");
  await expect(page.getByRole("region", { name: "Published" })).toContainText("Publish a design process guide");
  await page.getByRole("button", { name: "SEO/Content" }).click();
  await expect(page.getByLabel("Stage for Publish a design process guide")).toHaveValue("published");
  await page.getByRole("button", { name: "SEM" }).click();
  await expect(page.getByRole("region", { name: "SEM summary" })).toContainText("not live Google Ads bid data");
  await expect(page.getByRole("region", { name: "Ad group details for Test the keyword: design studio" })).toContainText("Design Studio intent");
  await page.getByRole("button", { name: "Accept" }).click();
  await expect(page.getByRole("region", { name: "SEM summary" })).toContainText("1 accepted");
  await page.getByRole("button", { name: "Organizer" }).click();
  await expect(page.getByRole("region", { name: "Backlog" })).toContainText("Test the keyword: design studio");
});

test("rescan → open Report history → compare two Reports", async ({ page }) => {
  await page.addInitScript(() => localStorage.setItem("trellis_access_token", "e2e-token"));
  await page.route("**/api/v1/websites", (route) => route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify({ data: { id: 12, url: "https://example.com", business_name: "Example", business_context: null, google_ads_connected: false, ga4_connected: false } }) }));
  let runNumber = 0;
  const analysis = (id: number, score: number) => ({ id, website_id: 12, status: "completed", last_completed_stage: "generating", pages_scanned_count: 2, error_message: null, started_at: "2026-09-07T12:00:00Z", completed_at: "2026-09-07T12:01:00Z", keywords: [], suggestions: [], technical_audit: { summary: "", findings: [] }, sem_summary: { candidate_count: 0, accepted_count: 0, cost_tier_counts: { low: 0, medium: 0, high: 0 }, estimated_cost_range: null, cost_tier_disclosure: "Estimate", campaign_boundary: "Planning only" }, health_score: score, health_score_delta: id === 31 ? null : 10, health_score_history: [], health_score_disclosure: "Organic only" });
  await page.route("**/api/v1/websites/12/analysis-runs", (route) => { runNumber += 1; const item = runNumber === 1 ? analysis(31, 50) : analysis(32, 60); return route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ data: item }) }); });
  const report = (id: number, score: number, date: string) => ({ id, website_id: 12, analysis_run_id: id + 30, generated_at: date, summary_text: `Health Score ${score}.`, health_score: score, health_score_delta: null, aeo_completion_pct: 0, aeo_completion_delta: null, technical_findings_resolved: 0, technical_findings_open: 1, content_published_count: 0, top_keywords: [], sem_accepted_count: 0, sem_cost_tier_breakdown: { low: 0, medium: 0, high: 0 }, ad_groups_defined_count: 0, organizer_stage_counts: { backlog: 0, in_production: 0, in_review: 0, published: 0 }, disclosure: "Saved snapshot: these KPI values will not change later." });
  const first = report(1, 50, "2026-08-07T12:00:00Z"), second = report(2, 60, "2026-09-07T12:00:00Z");
  await page.route("**/api/v1/websites/12/reports", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: runNumber > 1 ? [second, first] : [first] }) }));
  await page.route("**/api/v1/websites/12/report-comparison?**", (route) => route.fulfill({ contentType: "application/json", body: JSON.stringify({ data: { before: first, after: second, deltas: { health_score: { absolute: 10, percentage: 20 }, top_keywords: { added: [], removed: [] } } } }) }));
  await page.goto("/"); await page.getByLabel("Website URL").fill("example.com"); await page.getByLabel("Business or organization name").fill("Example"); await page.getByRole("button", { name: "Create workspace" }).click();
  await page.getByRole("button", { name: "Analyze website" }).click(); await expect(page.getByRole("heading", { name: "50/100" })).toBeVisible();
  await page.getByRole("button", { name: "Rescan website" }).click(); await expect(page.getByRole("heading", { name: "60/100" })).toBeVisible();
  await page.getByRole("button", { name: "Reports" }).click(); await expect(page.getByRole("heading", { name: "Report history" })).toBeVisible();
  await page.getByRole("button", { name: /Aug 7, 2026/ }).click(); await expect(page.getByTestId("current-report-summary")).toHaveText("Health Score 50.");
  await page.getByRole("button", { name: "Compare Reports" }).click(); await expect(page.getByRole("region", { name: "Report comparison" })).toContainText("+10 (+20.0%)");
});

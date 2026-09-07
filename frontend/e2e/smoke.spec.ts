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

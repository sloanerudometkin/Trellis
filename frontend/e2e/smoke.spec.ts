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
  const analysis = (status: string) => ({
    id: 31, website_id: 12, status,
    last_completed_stage: status === "completed" ? "generating" : null,
    pages_scanned_count: status === "completed" ? 2 : 0,
    error_message: null,
    started_at: "2026-09-06T12:00:00Z",
    completed_at: status === "completed" ? "2026-09-06T12:01:00Z" : null,
    keywords: status === "completed" ? [{ phrase: "design studio", frequency: 4, tfidf_score: 0.9 }] : [],
    suggestions: status === "completed" ? [
      { id: 1, category: "aeo", title: "Answer the core design question", description: "Add a concise answer below the homepage heading.", rationale: "A direct answer helps visitors and answer engines understand the studio.", priority: "high", stage: "suggested", status: "pending", affected_page_url: "https://example.com/", starter_outline: null, target_keywords: [] },
      { id: 2, category: "seo_content", title: "Publish a design process guide", description: "Explain the studio’s process in a practical guide.", rationale: "This fills an information gap for prospective clients.", priority: "medium", stage: "suggested", status: "pending", affected_page_url: null, starter_outline: ["Discovery", "Design", "Delivery"], target_keywords: [{ phrase: "design studio", recommended_usage_count: 4 }] },
    ] : [],
  });
  await page.route("**/api/v1/websites/12/analysis-runs", async (route) => {
    await route.fulfill({ status: 202, contentType: "application/json", body: JSON.stringify({ data: analysis("queued") }) });
  });
  await page.route("**/api/v1/analysis-runs/31", async (route) => {
    const statuses = ["scraping", "analyzing", "generating", "completed"];
    const status = statuses[Math.min(pollCount++, statuses.length - 1)];
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: analysis(status) }) });
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
});

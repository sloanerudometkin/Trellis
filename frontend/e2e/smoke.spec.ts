import { expect, test } from "@playwright/test";

test("authenticated user creates and navigates a website workspace", async ({ page }) => {
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

  await page.goto("/");
  await page.getByLabel("Website URL").fill("example.com");
  await page.getByLabel("Business or organization name").fill("Example Studio");
  await page.getByLabel(/Business context/).fill("Independent design studio");
  await page.getByRole("button", { name: "Create workspace" }).click();

  await expect(page.getByRole("navigation", { name: "Workspace views" })).toBeVisible();
  await page.getByRole("button", { name: "Organizer" }).click();
  await expect(page.getByRole("heading", { name: "Organizer", exact: true })).toBeVisible();
});

import { expect, test } from "@playwright/test";

test("opens a page in the test browser", async ({ page }) => {
  await page.setContent("<main><h1>Trellis</h1></main>");

  await expect(page.getByRole("heading", { name: "Trellis" })).toBeVisible();
});

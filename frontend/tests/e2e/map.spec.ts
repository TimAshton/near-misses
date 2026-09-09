import { test, expect } from "@playwright/test";

test("map page renders markers and opens a detail preview on click", async ({ page }) => {
  await page.goto("/map");

  const tokenMissing = page.getByTestId("mapbox-token-missing");
  if (await tokenMissing.isVisible().catch(() => false)) {
    test.skip(true, "VITE_MAPBOX_TOKEN not configured in this environment");
  }

  await expect(page.getByTestId("incident-map")).toBeVisible();
  await expect(page.getByTestId("filter-panel")).toBeVisible();

  const marker = page.getByTestId("incident-marker").first();
  await expect(marker).toBeVisible({ timeout: 15000 });
  await marker.click();

  await expect(page.getByTestId("incident-preview-modal")).toBeVisible();
  await page.getByTestId("incident-preview-detail-link").click();
  await expect(page).toHaveURL(/\/incidents\//);
});

test("map filter panel updates category filter", async ({ page }) => {
  await page.goto("/map");
  const filterPanel = page.getByTestId("filter-panel");
  await expect(filterPanel).toBeVisible();
  await page.getByTestId("filter-category").selectOption("aviation");
  await expect(page.getByTestId("filter-category")).toHaveValue("aviation");
});

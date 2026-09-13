import { test, expect } from "@playwright/test";

test("map page renders markers and opens a detail preview on click", async ({ page }) => {
  await page.goto("/map");

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

test("search start slider moves the From date backward and updates the date field", async ({
  page,
}) => {
  await page.goto("/map");
  const slider = page.getByTestId("filter-date-from-slider");
  await expect(slider).toBeVisible();

  const before = await page.getByTestId("filter-date-from").inputValue();
  await slider.fill("365"); // drag halfway back toward "365 days ago"
  const after = await page.getByTestId("filter-date-from").inputValue();

  expect(after).not.toBe(before);
  expect(new Date(after).getTime()).toBeLessThan(Date.now());
});

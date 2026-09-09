import { test, expect } from "@playwright/test";

test("dashboard shows stats, charts, and supports window toggles", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page.getByTestId("stat-total")).toBeVisible();
  await expect(page.getByTestId("timeline-chart")).toBeVisible();
  await expect(page.getByTestId("severity-breakdown")).toBeVisible();
  await expect(page.getByTestId("top-states-table")).toBeVisible();

  await page.getByTestId("window-7d").click();
  await expect(page.getByTestId("window-7d")).toHaveClass(/bg-blue-600/);

  await page.getByTestId("window-30d").click();
  await expect(page.getByTestId("window-30d")).toHaveClass(/bg-blue-600/);
});

test("manual refresh button triggers a poll", async ({ page }) => {
  await page.goto("/dashboard");
  const button = page.getByTestId("refresh-button");
  await button.click();
  // Button reflects a loading state immediately, then returns to idle once the poll completes.
  await expect(button).toBeEnabled({ timeout: 15000 });
});

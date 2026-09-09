import { test, expect } from "@playwright/test";

test("home page shows summary stats and quick links", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "US Incident Map" })).toBeVisible();
  await expect(page.getByTestId("stat-total")).toBeVisible();
  await expect(page.getByTestId("stat-last-updated")).toBeVisible();
  await expect(page.getByTestId("stat-categories")).toBeVisible();

  await expect(page.getByRole("link", { name: "Open Map" })).toBeVisible();
  await expect(page.getByRole("link", { name: "Open Dashboard" })).toBeVisible();
});

test("nav links route between pages", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("nav-links").getByRole("link", { name: "Map" }).click();
  await expect(page).toHaveURL(/\/map$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "Dashboard" }).click();
  await expect(page).toHaveURL(/\/dashboard$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "Reports" }).click();
  await expect(page).toHaveURL(/\/reports$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "About" }).click();
  await expect(page).toHaveURL(/\/about$/);
});

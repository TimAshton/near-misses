import { test, expect } from "@playwright/test";

test("root path renders the dashboard", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
  await expect(page.getByTestId("stat-total")).toBeVisible();
  await expect(page.getByTestId("timeline-chart")).toBeVisible();
});

test("legacy /dashboard path redirects to root", async ({ page }) => {
  await page.goto("/dashboard");

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "Dashboard" })).toBeVisible();
});

test("nav links route between pages", async ({ page }) => {
  await page.goto("/");
  await page.getByTestId("nav-links").getByRole("link", { name: "Map" }).click();
  await expect(page).toHaveURL(/\/map$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "Reports" }).click();
  await expect(page).toHaveURL(/\/reports$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "About" }).click();
  await expect(page).toHaveURL(/\/about$/);

  await page.getByTestId("nav-links").getByRole("link", { name: "Dashboard" }).click();
  await expect(page).toHaveURL(/\/$/);
});

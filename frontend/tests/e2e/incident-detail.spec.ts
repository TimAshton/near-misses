import { test, expect } from "@playwright/test";

test("incident detail page shows normalized fields, raw data, and source link", async ({ page }) => {
  await page.goto("/reports");

  const firstRow = page.getByTestId("incident-row").first();
  await expect(firstRow).toBeVisible({ timeout: 15000 });
  await firstRow.getByRole("link", { name: "View" }).click();

  await expect(page).toHaveURL(/\/incidents\//);
  await expect(page.getByTestId("incident-pin-map")).toBeVisible();

  const fields = page.getByTestId("incident-fields");
  await expect(fields.getByText("Category")).toBeVisible();
  await expect(fields.getByText("Occurred")).toBeVisible();

  await page.getByTestId("raw-data-toggle").click();
  await expect(page.getByTestId("raw-data-content")).toBeVisible();

  await expect(page.getByRole("link", { name: /View original source/ })).toBeVisible();
});

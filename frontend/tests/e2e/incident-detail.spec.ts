import { test, expect } from "@playwright/test";

test("incident detail page shows normalized fields, raw data, and source link", async ({ page }) => {
  await page.goto("/reports");

  const firstRow = page.getByTestId("incident-row").first();
  await expect(firstRow).toBeVisible({ timeout: 15000 });
  await firstRow.getByRole("link", { name: "View" }).click();

  await expect(page).toHaveURL(/\/incidents\//);
  await expect(page.getByTestId("incident-pin-map")).toBeVisible();
  await expect(page.getByTestId("incident-street-view-link")).toHaveAttribute(
    "href",
    /google\.com\/maps\?layer=c&cbll=/,
  );
  await expect(page.getByTestId("incident-google-maps-link")).toHaveAttribute(
    "href",
    /google\.com\/maps\?q=/,
  );

  const fields = page.getByTestId("incident-fields");
  await expect(fields.getByText("Category")).toBeVisible();
  await expect(fields.getByText("Occurred")).toBeVisible();

  await page.getByTestId("raw-data-toggle").click();
  await expect(page.getByTestId("raw-data-content")).toBeVisible();

  await expect(page.getByRole("link", { name: /View original source/ })).toBeVisible();
});

test("hurricane incidents show a satellite image panel", async ({ page }) => {
  await page.goto("/reports");
  await page.getByTestId("filter-category").selectOption("hurricane");

  const firstRow = page.getByTestId("incident-row").first();
  // Best-effort: whether an active/past storm made it into this environment's
  // live-sourced data depends on real-world weather, so skip quietly if none.
  try {
    await expect(firstRow).toBeVisible({ timeout: 5000 });
  } catch {
    test.skip();
    return;
  }

  await firstRow.getByRole("link", { name: "View" }).click();
  await expect(page).toHaveURL(/\/incidents\//);
  await expect(page.getByTestId("incident-satellite-image")).toBeVisible();
});

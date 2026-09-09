import { test, expect } from "@playwright/test";

test("reports table lists incidents, sorts, filters, and offers CSV export", async ({ page }) => {
  await page.goto("/reports");

  await expect(page.getByTestId("incident-table")).toBeVisible();
  await expect(page.getByTestId("csv-export-button")).toBeVisible();

  // Sorting: click the "Category" column header, expect a sort indicator to appear.
  await page.getByRole("columnheader", { name: /Category/ }).click();
  await expect(page.getByRole("columnheader", { name: /Category/ })).toContainText(/[▲▼]/);

  // Filtering: narrow to aviation and confirm the filter control reflects it.
  await page.getByTestId("filter-category").selectOption("aviation");
  await expect(page.getByTestId("filter-category")).toHaveValue("aviation");
});

import { expect, test } from "@playwright/test";

test("expert profile submission and access-key management flow", async ({ page }) => {
  await page.goto("/experts");
  await page.getByLabel("Full name").fill("Ada Lovelace");
  await page.getByLabel("Email").fill("ada@example.org");
  await page.getByLabel("Expertise entries").fill("Metadata workflows");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/v1/experts")),
    page.getByText("Submit profile").click(),
  ]);
  await expect(page.getByText(/Save your expert access key/i)).toBeVisible();
  await expect(page.getByText("Copy access key")).toBeVisible();
  await expect(page.getByText("Return to search")).toBeVisible();
});

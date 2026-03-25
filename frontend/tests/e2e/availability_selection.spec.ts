import { expect, test } from "@playwright/test";

test("slot count display and selection UI appear", async ({ page }) => {
  await page.goto("/experts");
  await page.getByLabel("Full name").fill("Ada Lovelace");
  await page.getByLabel("Email").fill("ada@example.org");
  await page.getByLabel("Expertise entries").fill("Metadata workflows");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/v1/experts")),
    page.getByText("Submit profile").click(),
  ]);

  await page.goto("/");
  await page.getByLabel("Your question").fill("metadata workflows");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/v1/match-queries")),
    page.getByLabel("Find experts").click(),
  ]);

  await page.getByLabel("Your name").fill("Grace Hopper");
  await page.getByLabel("Your email").fill("grace@example.org");
  await page.getByLabel("Select").check();
  await expect(page.getByText("Draft outreach")).toBeVisible();
});

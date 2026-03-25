import { expect, test } from "@playwright/test";

test("requester can search and draft outreach", async ({ page }) => {
  await page.goto("/experts");
  await page.getByLabel("Full name").fill("Ada Lovelace");
  await page.getByLabel("Email").fill("ada@example.org");
  await page.getByLabel("Expertise entries").fill("Research workflows");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/v1/experts")),
    page.getByText("Submit profile").click(),
  ]);

  await page.goto("/");
  await page.getByLabel("Your question").fill("I need advice on research workflows.");
  await Promise.all([
    page.waitForResponse((response) => response.url().includes("/api/v1/match-queries")),
    page.getByLabel("Find experts").click(),
  ]);

  await expect(page.getByText("Ada Lovelace")).toBeVisible();
  await page.getByLabel("Your name").fill("Grace Hopper");
  await page.getByLabel("Your email").fill("grace@example.org");
});

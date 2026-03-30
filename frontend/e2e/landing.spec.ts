import { expect, test } from "@playwright/test";

test("inicio muestra CTA de ingreso", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /estacionamiento/i })).toBeVisible();
  await expect(page.getByRole("link", { name: /registrar ingreso/i })).toBeVisible();
});

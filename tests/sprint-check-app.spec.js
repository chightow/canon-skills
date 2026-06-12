// @ts-check
const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:8423';

test.describe('board modal', () => {
  test('no Description tab on any ticket', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');

    const firstCard = page.locator('.card').first();
    await firstCard.click();
    await page.waitForSelector('#m-docs', { timeout: 5000 });

    const tabLabels = await page.locator('#m-docs .doc-tab').allTextContents();
    expect(tabLabels.map(t => t.trim())).not.toContain('Description');
  });

  test('first doc tab is active on open (ticket with docs)', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');

    // Use the in-progress sprint ticket which always has acceptance + plan docs
    const inProgressCard = page.locator('.card[data-id="t-f41d"]');
    await inProgressCard.click();
    await page.waitForSelector('#m-docs .doc-tab.active', { timeout: 5000 });

    const activeTab = page.locator('#m-docs .doc-tab.active').first();
    await expect(activeTab).toBeVisible();
    await expect(page.locator('#m-body')).not.toBeEmpty();
  });

  test('"No description." placeholder is gone', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');

    const firstCard = page.locator('.card').first();
    await firstCard.click();
    await page.waitForSelector('#m-body', { timeout: 5000 });

    await expect(page.locator('#m-body')).not.toContainText('No description.');
  });

  test('create-ticket textarea has updated placeholder', async ({ page }) => {
    await page.goto(BASE);
    await page.waitForLoadState('networkidle');

    await page.locator('#btn-create').click();
    await page.waitForSelector('#create-modal', { timeout: 3000 });

    const textarea = page.locator('#create-modal textarea');
    const placeholder = await textarea.getAttribute('placeholder');
    expect(placeholder).not.toMatch(/^Description$/i);
  });
});

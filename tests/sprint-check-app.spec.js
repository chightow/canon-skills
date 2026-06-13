// @ts-check
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

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

  test('doc-less tickets render ticket body in read-only modal', async ({ page }) => {
    const title = `Doc-less modal body check ${Date.now()}`;
    let createdId = '';

    try {
      await page.goto(BASE);
      await page.waitForLoadState('networkidle');

      await page.locator('#btn-create').click();
      await page.waitForSelector('#create-modal', { timeout: 3000 });
      await page.locator('#c-title').fill(title);
      await page.locator('#c-body').fill('## Context\nTicket body should render without sprint docs.\n\n## Notes\n- Uses existing markdown renderer');
      await page.locator('#c-submit').click();

      const card = page.locator('.card', { hasText: title });
      await expect(card).toBeVisible();
      createdId = await card.getAttribute('data-id') || '';
      await card.click();

      await expect(page.locator('#m-docs .doc-tab')).toHaveCount(0);
      await expect(page.locator('#m-body')).toContainText('Ticket body should render without sprint docs.');
      await expect(page.locator('#m-body')).toContainText('Uses existing markdown renderer');
      await expect(page.locator('.section-jump-link', { hasText: 'Context' })).toBeVisible();
    } finally {
      if (createdId) {
        fs.rmSync(path.join(process.cwd(), '.tickets', createdId), { recursive: true, force: true });
      }
    }
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

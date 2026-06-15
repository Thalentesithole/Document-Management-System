import { test, expect } from '@playwright/test';

test.describe('Documents Listing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/documents');
  });

  test('renders documents table headers', async ({ page }) => {
    await expect(page.getByText('Vendor')).toBeVisible();
    await expect(page.getByText('Amount')).toBeVisible();
    await expect(page.getByText('Status')).toBeVisible();
  });

  test('search input exists', async ({ page }) => {
    await expect(page.getByPlaceholder('Search documents...')).toBeVisible();
  });
});

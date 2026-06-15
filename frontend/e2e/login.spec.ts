import { test, expect } from '@playwright/test';

test.describe('Login & Registration Flow', () => {
  test('should display login form initially', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('heading', { name: 'InvoiceAI' })).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeVisible();
  });

  test('should toggle to register form', async ({ page }) => {
    await page.goto('/login');
    await page.getByText('Register').click();
    await expect(page.getByPlaceholder('John Doe')).toBeVisible();
    await expect(page.getByRole('button', { name: 'Register' })).toBeVisible();
  });

  test('shows validation error on invalid login', async ({ page }) => {
    await page.goto('/login');
    await page.getByPlaceholder('you@example.com').fill('invalid@test.com');
    await page.getByPlaceholder('••••••••').fill('wrongpassword');
    await page.getByRole('button', { name: 'Sign in' }).click();
    
    // Assume toast or inline error appears
    await expect(page.locator('text=Incorrect email or password')).toBeVisible({ timeout: 5000 });
  });
});

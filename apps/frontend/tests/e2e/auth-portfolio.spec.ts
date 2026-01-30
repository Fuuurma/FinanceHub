import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    await expect(page).toHaveTitle(/Login/);
    await expect(page.locator('h1')).toContainText('Sign In');
  });

  test('should show validation errors for empty fields', async ({ page }) => {
    await page.goto('/login');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Email is required')).toBeVisible();
    await expect(page.locator('text=Password is required')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Welcome')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[name="email"]', 'invalid@example.com');
    await page.fill('input[name="password"]', 'wrongpass');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });
});

test.describe('Portfolio', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display portfolio overview', async ({ page }) => {
    await page.goto('/portfolio');

    await expect(page.locator('text=Total Value')).toBeVisible();
    await expect(page.locator('text=Holdings')).toBeVisible();
    await expect(page.locator('text=Performance')).toBeVisible();
  });

  test('should add new holding', async ({ page }) => {
    await page.goto('/portfolio');
    await page.click('text=Add Holding');

    await page.fill('input[name="symbol"]', 'AAPL');
    await page.fill('input[name="quantity"]', '10');
    await page.fill('input[name="price"]', '150');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Holding added successfully')).toBeVisible();
  });

  test('should export portfolio data', async ({ page }) => {
    await page.goto('/portfolio');

    // Start waiting for download
    const downloadPromise = page.waitForEvent('download');
    await page.click('text=Export');
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/\.(csv|xlsx)$/);
  });
});

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpass123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
  });

  test('should display market overview', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page.locator('text=S&P 500')).toBeVisible();
    await expect(page.locator('text=Dow Jones')).toBeVisible();
    await expect(page.locator('text=NASDAQ')).toBeVisible();
  });

  test('should display portfolio performance chart', async ({ page }) => {
    await page.goto('/dashboard');

    // Wait for chart to render
    await page.waitForSelector('canvas', { timeout: 5000 });
    await expect(page.locator('canvas')).toBeVisible();
  });

  test('should navigate to portfolio details', async ({ page }) => {
    await page.goto('/dashboard');
    await page.click('text=View Portfolio');

    await expect(page).toHaveURL('/portfolio');
  });
});

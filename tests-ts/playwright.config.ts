import path from 'path';
import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';

// Завантажуємо .env з кореня репозиторію (HUB_login/.env)
dotenv.config({ path: path.join(__dirname, '..', '.env') });

const baseURL = process.env.TEST_BASE_URL || process.env.TEST_LOGIN_URL?.replace(/\/user\/login\/?$/, '') || 'https://hubtest.kasta.ua';

// Репорти як у Python: папка report_YYYYMMDD_HHMMSS (історія прогонів), last_failure_bug_report.txt при падінні
const now = new Date();
const YYYYMMDD = now.toISOString().slice(0, 10).replace(/-/g, '');
const HHMMSS = now.toTimeString().slice(0, 8).replace(/:/g, '');
const reportFolder = `report_${YYYYMMDD}_${HHMMSS}`;
const reportsDir = path.join(__dirname, '..', 'reports');

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: [
    ['html', { outputFolder: path.join(reportsDir, reportFolder), open: 'never' }],
    ['list'],
    ['./reporters/bug-report-reporter.ts', { reportsDir, currentReportFolder: reportFolder }],
    [
      'allure-playwright',
      {
        resultsDir: path.join(reportsDir, 'allure-results'),
        detail: true,
        suiteTitle: true,
      },
    ],
  ],
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
    viewport: { width: 1920, height: 1080 },
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
  outputDir: path.join(__dirname, '..', 'test-results'),
});

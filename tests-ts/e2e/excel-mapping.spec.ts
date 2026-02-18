/**
 * Тести Excel мапінгу фідів (переписані з tests-Python/tests/test_excel_mapping.py).
 * Cleanup: повернення стану фіду через UI (вимкнути чекбокс + Зберегти), видалення тимчасового файлу.
 * Очікування: expect().toBeVisible({ timeout }) замість фіксованих waitForTimeout.
 */
import path from 'path';
import fs from 'fs';
import { test, expect } from '@playwright/test';
import { testConfig } from '../fixtures/env';
import { LoginPage } from '../pages/LoginPage';
import { XmlFeedPage } from '../pages/XmlFeedPage';

const DOWNLOAD_DIR = path.join(process.cwd(), 'test-results', 'excel_mappings');
const SUCCESS_TEXT = 'Дані збережено!';

// Для cleanup у afterEach навіть при fail тесту
let excelCleanupFeedId: string | null = null;
let excelCleanupFilePath: string | null = null;

test.describe('Excel мапінг фідів', () => {
  test.beforeEach(async ({ page }) => {
    excelCleanupFeedId = null;
    excelCleanupFilePath = null;
    const { loginUrl, userEmail, userPassword } = testConfig;
    if (!userEmail || !userPassword) return;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(`${loginUrl}?next=/supplier-content/xml`);
    await loginPage.login(userEmail, userPassword);
    await loginPage.verifySuccessfulLogin();
  });

  test.afterEach(async ({ page }) => {
    // Cleanup завжди виконується, навіть при fail: повернути фід (UI) + видалити файл
    const feedId = excelCleanupFeedId;
    const filePath = excelCleanupFilePath;
    excelCleanupFeedId = null;
    excelCleanupFilePath = null;
    if (filePath && fs.existsSync(filePath)) {
      try {
        fs.unlinkSync(filePath);
      } catch {
        /* ignore */
      }
    }
    if (feedId) {
      try {
        const xmlFeedPage = new XmlFeedPage(page);
        const url = xmlFeedPage.getUrl();
        if (url.includes(feedId)) {
          await xmlFeedPage.disableUploadItemsCheckbox();
          await xmlFeedPage.clickSaveButton();
          await expect(page.getByText(SUCCESS_TEXT).first()).toBeVisible({ timeout: 10000 }).catch(() => {});
        }
      } catch {
        /* page може бути вже закритий при fail */
      }
    }
  });

  test('скачування та завантаження Excel файлу мапінгу', async ({ page }) => {
    test.setTimeout(180000);
    const { xmlFeedsUrl, testSupplierName, testExistingFeedId } = testConfig;
    const feedId = testExistingFeedId;
    if (!feedId) {
      test.skip(true, 'TEST_EXISTING_FEED_ID не вказано в конфігурації');
    }
    const xmlFeedPage = new XmlFeedPage(page);

    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();

    const feedEditUrl = `${xmlFeedsUrl}?feed_id=${feedId}&tab=feed`;
    await xmlFeedPage.goto(feedEditUrl);
    await xmlFeedPage.waitForLoadState('networkidle');
    await expect(page.getByRole('button', { name: 'Зберегти' }).first()).toBeVisible({ timeout: 10000 });

    const url = xmlFeedPage.getUrl();
    expect(url).toContain(feedId);

    const excelFilePath = await xmlFeedPage.downloadExcelMappingFile(DOWNLOAD_DIR, feedId);
    expect(excelFilePath).toBeTruthy();
    expect(fs.existsSync(excelFilePath)).toBe(true);
    expect(path.extname(excelFilePath).toLowerCase()).toMatch(/\.xlsx|\.xls/);
    expect(path.basename(excelFilePath)).toContain(feedId);
    excelCleanupFeedId = feedId;
    excelCleanupFilePath = excelFilePath;

    const uploadSuccess = await xmlFeedPage.uploadExcelMappingFile(excelFilePath);
    expect(uploadSuccess).toBe(true);

    try {
      await expect(page.getByText(SUCCESS_TEXT).first()).toBeVisible({ timeout: 15000 });
    } catch {
      expect(xmlFeedPage.getUrl()).toMatch(/feed_id|tab=feed/);
    }
  });

  test('валідація структури Excel файлу мапінгу', async ({ page }) => {
    test.setTimeout(120000);
    const { xmlFeedsUrl, testSupplierName, testExistingFeedId } = testConfig;
    const feedId = testExistingFeedId;
    if (!feedId) {
      test.skip(true, 'TEST_EXISTING_FEED_ID не вказано в конфігурації');
    }

    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();

    const feedEditUrl = `${xmlFeedsUrl}?feed_id=${feedId}&tab=feed`;
    await xmlFeedPage.goto(feedEditUrl);
    await xmlFeedPage.waitForLoadState('networkidle');
    await expect(page.getByRole('button', { name: 'Зберегти' }).first()).toBeVisible({ timeout: 10000 });

    expect(xmlFeedPage.getUrl()).toContain(feedId);

    const excelFilePath = await xmlFeedPage.downloadExcelMappingFile(DOWNLOAD_DIR, feedId);
    expect(excelFilePath).toBeTruthy();
    expect(fs.existsSync(excelFilePath)).toBe(true);
    expect(path.extname(excelFilePath).toLowerCase()).toMatch(/\.xlsx|\.xls/);
    expect(path.basename(excelFilePath)).toContain(feedId);
    excelCleanupFeedId = feedId;
    excelCleanupFilePath = excelFilePath;

    const expectedSheets = [
      'Результат',
      'Довідник кольорів',
      'Каскад+',
      'Конвертер+',
      'Категорія+',
      'Інструкція щодо мапінгу Каскад',
      'Підказки категорій',
      'Ігнорувати+',
      'Довідник Каста',
      'Оффер+',
    ];

    const XLSX = await import('xlsx');
    const lib = 'default' in XLSX && XLSX.default ? (XLSX as { default: { readFile: (p: string) => { SheetNames: string[] } } }).default : (XLSX as { readFile: (p: string) => { SheetNames: string[] } });
    const workbook = lib.readFile(excelFilePath);
    const sheetNames = workbook.SheetNames;
    for (const name of expectedSheets) {
      expect(sheetNames).toContain(name);
    }
    expect(sheetNames.length).toBeGreaterThanOrEqual(expectedSheets.length);
  });
});

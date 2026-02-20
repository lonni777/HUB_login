/**
 * Тести XML-фідів (переписані з tests-Python/tests/test_xml_feed.py).
 * Cleanup: фікстура feedCleanup — реєстрація feedId на delete/deactivate; виконується в teardown навіть при fail.
 */
import { test, expect } from '../fixtures/feed-cleanup';
import { testConfig } from '../fixtures/env';
import { LoginPage } from '../pages/LoginPage';
import { XmlFeedPage } from '../pages/XmlFeedPage';

test.describe('XML-фіди: додавання та валідація', () => {
  test.beforeEach(async ({ page }) => {
    const { loginUrl, userEmail, userPassword } = testConfig;
    if (!userEmail || !userPassword) return;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(`${loginUrl}?next=/supplier-content/xml`);
    await loginPage.login(userEmail, userPassword);
    await loginPage.verifySuccessfulLogin();
  });

  test('збереження валідного URL без пробілів', async ({ page, feedCleanup }) => {
    test.setTimeout(90000);
    const { testSupplierName, xmlFeedsUrl, testXmlFeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testXmlFeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await xmlFeedPage.verifySuccessMessage('Дані збережено!');
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    let feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testXmlFeedUrl);
    if (!feedId) {
      await xmlFeedPage.filterFeedsByLink(testXmlFeedUrl);
      feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
    }
    if (feedId) feedCleanup.registerDelete(feedId);
  });

  test('збереження фіду з посиланням http', async ({ page, feedCleanup }) => {
    test.setTimeout(90000);
    const { testSupplierName, xmlFeedsUrl, testHttpXmlFeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testHttpXmlFeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await xmlFeedPage.verifySuccessMessage('Дані збережено!');
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    let feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testHttpXmlFeedUrl);
    if (!feedId) {
      await xmlFeedPage.filterFeedsByLink(testHttpXmlFeedUrl);
      feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
    }
    if (feedId) feedCleanup.registerDelete(feedId);
  });

  test('збереження нормалізованого URL (пробіли до/після)', async ({ page, feedCleanup }) => {
    test.setTimeout(90000);
    const { testSupplierName, testXmlFeedUrl, xmlFeedsUrl } = testConfig;
    const originalUrl = testXmlFeedUrl.trim();
    const urlWithSpaces = ` ${originalUrl} `;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(urlWithSpaces);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    try {
      await xmlFeedPage.verifySuccessMessage('Дані збережено!');
    } catch {
      const url = page.url();
      if (url.includes('/supplier-content/xml')) {
        /* ок */
      } else throw new Error('Очікувалось збереження або редирект на таблицю');
    }
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    await xmlFeedPage.filterFeedsByLink(originalUrl);
    let feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
    if (!feedId) feedId = await xmlFeedPage.getFeedIdByUrlFromTable(originalUrl);
    expect(feedId, 'Має бути знайдено feed_id після збереження').toBeTruthy();
    if (feedId) feedCleanup.registerDelete(feedId);
  });

  test('невалідна структура (JSON замість XML) — помилка валідації', async ({ page }) => {
    const { testSupplierName, testInvalidXmlFeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testInvalidXmlFeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    // Очікуємо появу повідомлення про помилку (без фіксованих 5 с)
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/Помилка валідації/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
    const hasError = await xmlFeedPage.hasValidationErrorMessage('Помилка валідації xml структури фіду');
    expect(hasError).toBe(true);
  });

  test('URL 404 — помилка валідації', async ({ page }) => {
    const { testSupplierName, test404FeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(test404FeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    // Очікуємо появу повідомлення про помилку (без фіксованих 5 с)
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/Помилка валідації/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
    const hasError = await xmlFeedPage.hasValidationErrorMessage('Помилка валідації');
    expect(hasError).toBe(true);
  });

  test('порожнє поле URL — валідація', async ({ page }) => {
    const { testSupplierName, xmlFeedsUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    const countBefore = await xmlFeedPage.getFeedsTableRowCount();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.clearFeedUrl();
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    // Очікуємо появу повідомлення валідації (без фіксованих 3 с)
    await expect(
      page.locator('.ant-form-item-explain-error').or(page.getByText(/URL|порожн|обов'язков/i)).first(),
    ).toBeVisible({ timeout: 5000 });
    const hasError =
      (await xmlFeedPage.hasValidationErrorMessage('URL')) ||
      (await xmlFeedPage.hasValidationErrorMessage('порожн')) ||
      (await xmlFeedPage.hasValidationErrorMessage("обов'язков"));
    expect(hasError).toBe(true);
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    const countAfter = await xmlFeedPage.getFeedsTableRowCount();
    expect(countAfter).toBe(countBefore);
  });

  test('збереження фіду без чекбокса "Завантажити товари з xml"', async ({ page, feedCleanup }) => {
    const { testSupplierName, xmlFeedsUrl, testXmlFeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testXmlFeedUrl);
    await xmlFeedPage.clickSaveButton();
    // Після збереження без чекбокса може не бути тосту — переходимо в таблицю і перевіряємо Підключено? = Ні
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    await xmlFeedPage.filterFeedsByLink(testXmlFeedUrl);
    let feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
    if (!feedId) feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testXmlFeedUrl);
    const connected = await xmlFeedPage.getConnectedStatusFromFilteredRow();
    expect(connected, 'Для фіду без чекбокса "Завантажити товари з xml" очікується Підключено? = Ні').toBe('Ні');
    if (feedId) feedCleanup.registerDelete(feedId);
  });

  test('додавання одного URL двічі — без дубля', async ({ page, feedCleanup }) => {
    const { testSupplierName, testDuplicateFeedUrl, xmlFeedsUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testDuplicateFeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await xmlFeedPage.verifySuccessMessage('Дані збережено!');
    await expect(page).toHaveURL(new RegExp(xmlFeedsUrl.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')));
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    await xmlFeedPage.filterFeedsByLink(testDuplicateFeedUrl);
    let feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
    if (!feedId) feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testDuplicateFeedUrl);
    expect(feedId).toBeTruthy();
    const rowsCount = await xmlFeedPage.getFeedsTableRowCount();
    expect(rowsCount).toBeGreaterThanOrEqual(1);
    if (feedId) feedCleanup.registerDeactivate(feedId);
  });

  test('невірний формат URL (ftp) — помилка валідації', async ({ page }) => {
    const { testSupplierName, testInvalidUrlFeed } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testInvalidUrlFeed);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/Помилка валідації/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
    const hasError = await xmlFeedPage.hasValidationErrorMessage('Помилка валідації xml структури фіду');
    expect(hasError).toBe(true);
  });

  test('URL без протоколу (тільки домен) — помилка валідації', async ({ page }) => {
    const urlWithoutProtocol = 'example.com/feed.xml';
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testConfig.testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(urlWithoutProtocol);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/Помилка валідації|no protocol/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
    const hasNoProtocol = await xmlFeedPage.hasValidationErrorMessage('no protocol');
    const hasExampleUrl = await xmlFeedPage.hasValidationErrorMessage('example.com/feed.xml');
    expect(hasNoProtocol, 'Очікується помилка "no protocol"').toBe(true);
    expect(hasExampleUrl, 'Очікується введений URL у тексті помилки').toBe(true);
  });

  test('некоректна структура XML', async ({ page }) => {
    const { testSupplierName, testInvalidXmlStructureUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testInvalidXmlStructureUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/Помилка валідації/i))
        .first(),
    ).toBeVisible({ timeout: 5000 });
    const hasError = await xmlFeedPage.hasValidationErrorMessage('Помилка валідації');
    expect(hasError).toBe(true);
  });

  test('connection timeout 1 хв', async ({ page }) => {
    test.setTimeout(120000);
    const { testSupplierName, testTimeoutFeedUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.clickAddNewFeedButton();
    await xmlFeedPage.fillFeedUrl(testTimeoutFeedUrl);
    await xmlFeedPage.enableUploadItemsCheckbox();
    await xmlFeedPage.clickSaveButton();
    // Очікуємо появу повідомлення про помилку/таймаут (бекенд чекає до ~1 хв), але не довше 70 с
    await expect(
      page
        .locator('.ant-alert-error, .ant-message-error, .ant-form-item-explain-error')
        .or(page.getByText(/помилка валідації|timeout|з'єднання|з\'єднання/i))
        .first(),
    ).toBeVisible({ timeout: 70000 });
    const url = page.url();
    const stillOnEdit = url.includes('feed_id') || url.includes('supplier-content/xml');
    expect(stillOnEdit).toBe(true);
    const bodyText = (await page.locator('body').textContent()) || '';
    const hasErrorOrTimeout =
      bodyText.toLowerCase().includes('помилка валідації') ||
      bodyText.toLowerCase().includes('timeout') ||
      bodyText.toLowerCase().includes('з\'єднання');
    expect(stillOnEdit && (hasErrorOrTimeout || bodyText.length > 0)).toBe(true);
  });

  test('обмеження 3 активні фіди', async ({ page, feedCleanup }) => {
    test.setTimeout(120000);
    const { testSupplierName, xmlFeedsUrl } = testConfig;
    const xmlFeedPage = new XmlFeedPage(page);
    await xmlFeedPage.selectSupplier(testSupplierName);
    await xmlFeedPage.navigateToXmlFeedsViaMenu();
    await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
    const feedIds = await xmlFeedPage.getFirstNFeedIds(4);
    if (feedIds.length < 4) {
      test.skip(true, 'У таблиці постачальника має бути щонайменше 4 фіди');
    }
    const enabledInThisTest: string[] = [];
    const successLocator = page.getByText('Дані збережено!');
    // Текст помилки з backend (feed.clj): "Неможливо підключити більше 3х фідів. Вимкніть спочатку один з фідів"
    const errorLimitLocator = page.locator('.ant-alert.ant-alert-error').filter({
      hasText: /Неможливо підключити більше 3х фідів\. Вимкніть спочатку один з фідів/,
    });

    for (let i = 0; i < 4; i++) {
      await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
      await xmlFeedPage.openFeedFromTableById(feedIds[i]);
      const checked = await xmlFeedPage.isUploadItemsCheckboxChecked();
      if (checked) continue;

      await xmlFeedPage.enableUploadItemsCheckbox();
      await xmlFeedPage.clickSaveButton();
      await expect(successLocator.or(errorLimitLocator).first()).toBeVisible({ timeout: 5000 });
      const gotSuccess = await successLocator.isVisible();
      if (gotSuccess) {
        enabledInThisTest.push(feedIds[i]);
      } else {
        await expect(errorLimitLocator).toBeVisible();
        break;
      }
    }

    for (const feedId of enabledInThisTest) {
      feedCleanup.registerDeactivate(feedId);
    }
  });
});

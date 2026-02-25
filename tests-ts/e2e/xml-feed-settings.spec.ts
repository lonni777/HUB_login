/**
 * Тести налаштувань XML-фідів (блок «Налаштування» на сторінці редагування фіду).
 * Один spec-файл — кілька тест-сьютів (describe) по кожній опції.
 * Cleanup: feedCleanup для фідів, створених у тестах.
 */
import { test, expect } from '../fixtures/feed-cleanup';
import { testConfig } from '../fixtures/env';
import { LoginPage } from '../pages/LoginPage';
import { XmlFeedPage } from '../pages/XmlFeedPage';

test.describe('XML-фіди: налаштування завантаження', () => {
  test.beforeEach(async ({ page }) => {
    const { loginUrl, userEmail, userPassword } = testConfig;
    if (!userEmail || !userPassword) return;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(`${loginUrl}?next=/supplier-content/xml`);
    await loginPage.login(userEmail, userPassword);
    await loginPage.verifySuccessfulLogin();
  });

  test.describe('Завантажити товари з xml (поведінка при увімк/вимк)', () => {
    test('активний фід завантажує новинки', async ({ page, feedCleanup }) => {
      test.setTimeout(120000);
      const { testSupplierName, xmlFeedsUrl, testXmlFeedUrl, triggerFeedloadUrl, triggerFeedloadAuth } =
        testConfig;
      const xmlFeedPage = new XmlFeedPage(page);

      await xmlFeedPage.selectSupplier(testSupplierName);
      await xmlFeedPage.navigateToXmlFeedsViaMenu();
      await xmlFeedPage.clickAddNewFeedButton();
      await xmlFeedPage.fillFeedUrl(testXmlFeedUrl);
      await xmlFeedPage.enableUploadItemsCheckbox();
      await xmlFeedPage.clickSaveButton();
      await xmlFeedPage.verifySuccessMessage('Дані збережено!');

      await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
      await xmlFeedPage.filterFeedsByLink(testXmlFeedUrl);
      let feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
      if (!feedId) feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testXmlFeedUrl);
      expect(feedId, 'Має бути знайдено feed_id після збереження').toBeTruthy();
      if (feedId) feedCleanup.registerDelete(feedId);

      if (triggerFeedloadAuth) {
        const feedUrlWithoutFragment = testXmlFeedUrl.replace(/#.*$/, '');
        const originUrl = `${feedUrlWithoutFragment}#ufeed${feedId}`;
        const response = await fetch(triggerFeedloadUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Authorization: triggerFeedloadAuth },
          body: JSON.stringify({ origin_url: originUrl }),
        });
        expect(
          response.ok,
          `trigger-feedload має повернути успішний статус, отримано: ${response.status}`,
        ).toBe(true);
        await page.waitForTimeout(15000);
      }
      // TODO: перевірка «товари з'явилися у Новинки» — потрібен URL/локатор сторінки Новинки або інший спосіб (репорт).
    });

    test('вимкнення фіда блокує нові завантаження', async ({ page, feedCleanup }) => {
      test.setTimeout(120000);
      const {
        testSupplierName,
        xmlFeedsUrl,
        testXmlFeedTwoVersionsUrl,
        triggerFeedloadUrl,
        triggerFeedloadAuth,
      } = testConfig;
      if (!triggerFeedloadAuth) {
        test.skip(true, 'потрібен TEST_TRIGGER_FEEDLOAD_AUTH для виклику trigger-feedload');
        return;
      }
      const xmlFeedPage = new XmlFeedPage(page);

      // 1. Створюємо фід з URL, що повертає спочатку 1 товар, потім 2 (mock на 9877)
      await xmlFeedPage.selectSupplier(testSupplierName);
      await xmlFeedPage.navigateToXmlFeedsViaMenu();
      await xmlFeedPage.clickAddNewFeedButton();
      await xmlFeedPage.fillFeedUrl(testXmlFeedTwoVersionsUrl);
      await xmlFeedPage.enableUploadItemsCheckbox();
      await xmlFeedPage.clickSaveButton();
      await xmlFeedPage.verifySuccessMessage('Дані збережено!');

      await xmlFeedPage.navigateToFeedsTable(xmlFeedsUrl);
      await xmlFeedPage.filterFeedsByLink(testXmlFeedTwoVersionsUrl);
      let feedId = await xmlFeedPage.getFeedIdFromFilteredTable();
      if (!feedId) feedId = await xmlFeedPage.getFeedIdByUrlFromTable(testXmlFeedTwoVersionsUrl);
      expect(feedId, 'Має бути знайдено feed_id').toBeTruthy();
      if (feedId) feedCleanup.registerDelete(feedId);

      const feedUrlForTrigger = testXmlFeedTwoVersionsUrl.replace(/#.*$/, '');
      const originUrl = `${feedUrlForTrigger}#ufeed${feedId}`;

      // 2. Перший trigger: бекенд завантажує фід → mock повертає 1 товар (blocked-test-1)
      let response = await fetch(triggerFeedloadUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: triggerFeedloadAuth },
        body: JSON.stringify({ origin_url: originUrl }),
      });
      expect(response.ok, `trigger-feedload 1: ${response.status}`).toBe(true);
      await page.waitForTimeout(15000);

      // 3. Вимикаємо «Завантажити товари з xml», зберігаємо
      await xmlFeedPage.openFeedForEditing(feedId!);
      await xmlFeedPage.disableUploadItemsCheckbox();
      await xmlFeedPage.clickSaveButton();
      await xmlFeedPage.verifySuccessMessage('Дані збережено!');

      // 4. Другий trigger: бекенд знову завантажує фід → mock повертає 2 товари; новий товар (blocked-test-2) не повинен імпортуватися
      response = await fetch(triggerFeedloadUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: triggerFeedloadAuth },
        body: JSON.stringify({ origin_url: originUrl }),
      });
      expect(response.ok, `trigger-feedload 2: ${response.status}`).toBe(true);
      await page.waitForTimeout(15000);

      // 5. Перевірка: на сторінці фіду / звіті не має з’являтися SKU blocked-test-2 (він лише в XML при другому запиті, імпорт має бути заблокований)
      await xmlFeedPage.openFeedForEditing(feedId!);
      await page.waitForTimeout(3000);
      const bodyText = (await page.locator('body').textContent()) || '';
      expect(
        bodyText.includes('blocked-test-2'),
        'При вимкненому «Завантажити товари з xml» новий товар (blocked-test-2) не повинен з’явитися у звіті/сторінці',
      ).toBe(false);
    });

    test('вимкнений фід призупиняє оновлення контенту', async ({ page, feedCleanup }) => {
      test.skip(true, 'фід з оновленням контенту → зняти чекбокс → змінити XML опис → значення не оновлюються');
    });

    test('вимкнений фід призупиняє оновлення цін/стоків (звичайний парсер)', async ({
      page,
      feedCleanup,
    }) => {
      test.skip(true, 'фід з оновленням цін/стоків (звичайний парсер) → зняти чекбокс → ціни/стоки не оновлюються');
    });

    test('вимкнений фід НЕ призупиняє оновлення цін/стоків (новий парсер)', async ({
      page,
      feedCleanup,
    }) => {
      test.skip(true, 'новий парсер — при вимкненому чекбоксі оновлення цін/стоків все одно виконуються');
    });
  });
});

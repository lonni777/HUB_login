import { test, expect } from '@playwright/test';
import { testConfig } from '../fixtures/env';
import { loginLocators } from '../locators/login.locators';
import { LoginPage } from '../pages/LoginPage';

test.describe('Авторизація в HUB', () => {
  test('успішний логін з валідними даними', async ({ page }) => {
    const { loginUrl, userEmail, userPassword, dashboardUrl } = testConfig;
    if (!userEmail || !userPassword) {
      test.skip(true, 'TEST_USER_EMAIL та TEST_USER_PASSWORD мають бути задані в .env');
    }
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.login(userEmail, userPassword);
    await loginPage.verifySuccessfulLogin(dashboardUrl || undefined);
  });

  test('логін з невірним паролем', async ({ page }) => {
    const { loginUrl, userEmail } = testConfig;
    if (!userEmail) test.skip(true, 'TEST_USER_EMAIL потрібен в .env');
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.attemptLogin(userEmail, 'wrong_password_123');
    await loginPage.verifyStayedOnLoginPage();
    const errorVisible = await loginPage.isErrorMessageVisible();
    if (errorVisible) {
      const text = await loginPage.getErrorMessageText();
      expect(text).toBeTruthy();
    }
  });

  test('логін з невалідним email (подвійна літера)', async ({ page }) => {
    const { loginUrl, userEmail, userPassword } = testConfig;
    if (!userEmail || !userPassword) test.skip(true, 'TEST_USER_EMAIL та TEST_USER_PASSWORD потрібні');
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    const invalidEmail = userEmail.includes('@')
      ? userEmail.replace('@', 'o@')
      : userEmail + 'o@kasta.ua';
    await loginPage.attemptLogin(invalidEmail, userPassword);
    await expect(page.locator(loginLocators.errorAlert)).toBeVisible({ timeout: 5000 });
    await loginPage.verifyStayedOnLoginPage();
    await loginPage.verifyErrorMessageContains('Невірний логін');
    await loginPage.verifyErrorMessageContains('Зверніться до адмінів');
  });

  test('логін з неіснуючим користувачем', async ({ page }) => {
    const { loginUrl } = testConfig;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.attemptLogin('i.i.kontent@gmail.com', 'Qwerty123');
    await expect(page.locator(loginLocators.errorAlert)).toBeVisible({ timeout: 5000 });
    await expect(page).toHaveURL(/supplier-reg=true/);
    const errorVisible = await loginPage.isErrorMessageVisible();
    expect(errorVisible).toBe(true);
    const errorText = await loginPage.getErrorMessageText();
    expect(errorText.toLowerCase()).toContain('такого користувача не існує');
    expect(errorText.toLowerCase()).toMatch(/зареєструйте|заповнивши/);
  });

  test('логін з деактивованим користувачем', async ({ page }) => {
    const { loginUrl } = testConfig;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.attemptLogin('i.i.kontent+test123@gmail.com', 'Qwerty123');
    await expect(page).toHaveURL(/supplier-reg=true/, { timeout: 5000 });
    const bodyText = (await page.locator('body').textContent()) || '';
    const expectedParts = ['вітаємо', 'зареєстровані', 'kasta.ua', 'реєстраці', 'hub', 'заповніть'];
    const found = expectedParts.filter((p) => bodyText.toLowerCase().includes(p));
    expect(found.length).toBeGreaterThanOrEqual(4);
  });

  async function testSqlInjectionPayload(
    page: import('@playwright/test').Page,
    payload: string,
  ): Promise<void> {
    const { loginUrl, userPassword } = testConfig;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.attemptLogin(payload, userPassword);
    await expect(page).toHaveURL(/\/(user\/login|supplier-reg|\?)/, { timeout: 5000 });
    const url = page.url();
    expect(url).toMatch(/\/(user\/login|supplier-reg|\?)/);
    const title = await page.title();
    expect(title).toBeTruthy();
  }

  test('SQL injection: базові OR з коментарями', async ({ page }) => {
    const payloads = ["' OR '1'='1", "' OR '1'='1' --", "' OR '1'='1' /*", "' OR '1'='1' #"];
    for (const payload of payloads) {
      await testSqlInjectionPayload(page, payload);
    }
  });

  test('SQL injection: числові та рядкові порівняння', async ({ page }) => {
    const payloads = ["' OR 1=1--", "' OR 'a'='a", "' OR 1=1#", "1' OR '1'='1"];
    for (const payload of payloads) {
      await testSqlInjectionPayload(page, payload);
    }
  });

  test('SQL injection: валідні дані + UNION', async ({ page }) => {
    const payloads = ["admin'--", "admin'/*", "admin' OR '1'='1", "' UNION SELECT NULL--"];
    for (const payload of payloads) {
      await testSqlInjectionPayload(page, payload);
    }
  });

  test('логін з пустими полями', async ({ page }) => {
    const { loginUrl } = testConfig;
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await page.waitForLoadState('networkidle');
    const emailVal = await page.locator(loginLocators.emailInput).inputValue();
    const passVal = await page.locator(loginLocators.passwordInput).inputValue();
    expect(emailVal).toBe('');
    expect(passVal).toBe('');
    const btnEnabled = await loginPage.isLoginButtonEnabled();
    expect(btnEnabled).toBe(true);
    await page.locator(loginLocators.loginButton).click();
    await expect(
      page.locator(loginLocators.fieldValidationError).or(page.getByText("Обов'язкове поле")).first(),
    ).toBeVisible({ timeout: 5000 });
    await loginPage.verifyStayedOnLoginPage();
    const validationVisible = await loginPage.isFieldValidationErrorVisible();
    const bodyText = (await page.locator('body').textContent()) || '';
    const hasValidationText =
      /обов'язкове|обовязкове|заповніть|заповнити|required|поле/i.test(bodyText);
    expect(
      validationVisible || hasValidationText,
      'Очікувалось повідомлення валідації (Обов\'язкове поле / заповніть) або видимий елемент помилки',
    ).toBe(true);
  });

  test('логін тільки з email (без пароля)', async ({ page }) => {
    const { loginUrl, userEmail } = testConfig;
    if (!userEmail) test.skip(true, 'TEST_USER_EMAIL потрібен');
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.fillEmail(userEmail);
    const loginBtn = page.locator(loginLocators.loginButton);
    await expect(loginBtn).toBeVisible({ timeout: 2000 });
    const isDisabled = await loginBtn.isDisabled();
    if (isDisabled) {
      await loginPage.verifyStayedOnLoginPage();
      expect(isDisabled).toBe(true);
      return;
    }
    await loginPage.clickLoginButtonWithoutNavigation();
    await expect(
      page.locator(loginLocators.fieldValidationError).or(page.getByText("Обов'язкове поле")).first(),
    ).toBeVisible({ timeout: 5000 });
    await loginPage.verifyStayedOnLoginPage();
    const validationVisible = await loginPage.isFieldValidationErrorVisible();
    expect(validationVisible).toBe(true);
  });

  test('логін тільки з паролем (без email)', async ({ page }) => {
    const { loginUrl, userPassword } = testConfig;
    if (!userPassword) test.skip(true, 'TEST_USER_PASSWORD потрібен');
    const loginPage = new LoginPage(page);
    await loginPage.navigateToLogin(loginUrl);
    await loginPage.fillPassword(userPassword);
    const loginBtn = page.locator(loginLocators.loginButton);
    await expect(loginBtn).toBeVisible({ timeout: 2000 });
    const isDisabled = await loginBtn.isDisabled();
    if (isDisabled) {
      await loginPage.verifyStayedOnLoginPage();
      expect(isDisabled).toBe(true);
      return;
    }
    await loginPage.clickLoginButtonWithoutNavigation();
    await expect(
      page.locator(loginLocators.fieldValidationError).or(page.getByText("Обов'язкове поле")).first(),
    ).toBeVisible({ timeout: 5000 });
    await loginPage.verifyStayedOnLoginPage();
    const validationVisible = await loginPage.isFieldValidationErrorVisible();
    expect(validationVisible).toBe(true);
  });
});

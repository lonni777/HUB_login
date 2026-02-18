import { expect } from '@playwright/test';
import { BasePage } from './BasePage';
import { loginLocators } from '../locators/login.locators';

export class LoginPage extends BasePage {
  async navigateToLogin(url: string): Promise<void> {
    await this.goto(url);
  }

  async fillEmail(email: string): Promise<void> {
    await this.page.locator(loginLocators.emailInput).fill(email);
  }

  async fillPassword(password: string): Promise<void> {
    await this.page.locator(loginLocators.passwordInput).fill(password);
  }

  async clickLoginButton(): Promise<void> {
    await this.page.locator(loginLocators.loginButton).click();
  }

  async clickLoginButtonWithoutNavigation(): Promise<void> {
    await this.page.locator(loginLocators.loginButton).click();
    // Очікування результату (помилка/валідація) — у тестах через expect().toBeVisible({ timeout })
  }

  /** Повний логін з очікуванням навігації */
  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.page.locator(loginLocators.loginButton).click();
    await this.page.waitForLoadState('networkidle', { timeout: 15000 });
  }

  /** Спроба логіну без очікування навігації (негативні тести) */
  async attemptLogin(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.clickLoginButtonWithoutNavigation();
  }

  async verifySuccessfulLogin(expectedUrl?: string): Promise<void> {
    if (expectedUrl) {
      await expect(this.page).toHaveURL(expectedUrl, { timeout: 5000 });
    } else {
      const url = this.getUrl();
      expect(url).not.toContain('/user/login');
    }
  }

  async verifyStayedOnLoginPage(): Promise<void> {
    await expect(this.page).toHaveURL(/\/user\/login/);
  }

  async isErrorMessageVisible(): Promise<boolean> {
    try {
      const alert = this.page.locator(loginLocators.errorAlert);
      return await alert.isVisible({ timeout: 3000 });
    } catch {
      return false;
    }
  }

  async getErrorMessageText(): Promise<string> {
    try {
      const alert = this.page.locator(loginLocators.errorAlert);
      if (await alert.isVisible({ timeout: 2000 }))
        return (await alert.textContent()) || '';
    } catch {
      // ignore
    }
    return '';
  }

  async verifyErrorMessageContains(expectedText: string): Promise<void> {
    const visible = await this.isErrorMessageVisible();
    expect(visible, 'Повідомлення про помилку має бути видиме').toBe(true);
    const text = await this.getErrorMessageText();
    expect(text.toLowerCase()).toContain(expectedText.toLowerCase());
  }

  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.page.locator(loginLocators.loginButton).isEnabled();
  }

  async isFieldValidationErrorVisible(): Promise<boolean> {
    // Після натискання "Увійти" під полями (email, пароль) з’являється "Обов'язкове поле"
    try {
      const validationText = this.page.getByText("Обов'язкове поле").first();
      return await validationText.isVisible({ timeout: 2000 });
    } catch {
      /* ignore */
    }
    try {
      const validationText = this.page.getByText('Обовязкове поле').first();
      return await validationText.isVisible({ timeout: 1500 });
    } catch {
      /* ignore */
    }
    const selectors = [
      loginLocators.fieldValidationError,
      loginLocators.fieldValidationExplain,
      loginLocators.fieldValidationAny,
    ];
    for (const sel of selectors) {
      try {
        const el = this.page.locator(sel).first;
        if (await el.isVisible({ timeout: 1000 })) return true;
      } catch {
        /* ignore */
      }
    }
    return false;
  }

  get locators() {
    return loginLocators;
  }
}

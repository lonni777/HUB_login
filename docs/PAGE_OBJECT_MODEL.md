# Page Object Model (POM) — TypeScript

Проєкт e2e-тестів (tests-ts) побудований за патерном **Page Object Model**: локатори винесені окремо, логіка сторінок — у класи Page Objects, тести використовують лише ці об’єкти.

---

## Що таке POM?

Page Object Model — патерн, при якому:

- **Елементи сторінки** (селектори) зберігаються в окремих модулях (локатори).
- **Дії та перевірки** інкапсульовані в класи (Page Objects), які отримують `page: Page` і працюють через Playwright API.
- **Тести** створюють потрібні Page Objects і викликають їхні методи, без прямого використання селекторів у spec-файлах.

Переваги: один раз змінив локатор — оновили всі тести; тести короткі та читабельні; легко додавати нові сторінки.

---

## Структура tests-ts

```
tests-ts/
├── locators/           # Локатори (селектори)
│   ├── login.locators.ts
│   └── xml-feed.locators.ts
├── pages/              # Page Objects
│   ├── BasePage.ts
│   ├── LoginPage.ts
│   └── XmlFeedPage.ts
├── fixtures/           # Конфіг, фікстури (env, cleanup)
│   ├── env.ts
│   └── feed-cleanup.ts
├── e2e/                # Тести (specs)
│   ├── login.spec.ts
│   ├── xml-feed.spec.ts
│   └── excel-mapping.spec.ts
├── utils/
│   └── db-helper.ts
└── playwright.config.ts
```

---

## 1. Локатори (`locators/`)

Локатори — це об’єкти з селекторами (рядки або Playwright-ролі). Один файл на логічну сторінку/область.

**Приклад:** `locators/login.locators.ts`

```typescript
export const loginLocators = {
  emailInput: '#email',
  passwordInput: '#password',
  loginButton: "role=button[name='Увійти']",
  errorAlert: 'form .ant-alert.ant-alert-error',
  fieldValidationError: 'form .ant-form-item-explain-error',
  fieldValidationExplain: 'form .ant-form-item-explain',
  fieldValidationAny: '[class*="ant-form-item-explain"]',
} as const;
```

**Переваги:**

- Всі селектори в одному місці.
- Зміна локатора оновлює всі тести та Page Objects, що його використовують.

---

## 2. Page Objects (`pages/`)

### BasePage

Базовий клас з загальними методами: перехід за URL, поточний URL, очікування стану завантаження.

```typescript
// pages/BasePage.ts
import { Page } from '@playwright/test';

export class BasePage {
  constructor(protected page: Page) {}

  async goto(url: string): Promise<void> {
    await this.page.goto(url);
  }

  getUrl(): string {
    return this.page.url();
  }

  async waitForLoadState(state: 'load' | 'domcontentloaded' | 'networkidle' = 'networkidle'): Promise<void> {
    await this.page.waitForLoadState(state);
  }
}
```

### Сторінковий Page Object

Клас наслідує `BasePage`, імпортує локатори і інкапсулює дії та перевірки.

```typescript
// pages/LoginPage.ts
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

  async login(email: string, password: string): Promise<void> {
    await this.fillEmail(email);
    await this.fillPassword(password);
    await this.page.locator(loginLocators.loginButton).click();
    await this.page.waitForLoadState('networkidle', { timeout: 15000 });
  }

  async verifySuccessfulLogin(expectedUrl?: string): Promise<void> {
    if (expectedUrl) {
      await expect(this.page).toHaveURL(expectedUrl, { timeout: 5000 });
    } else {
      expect(this.getUrl()).not.toContain('/user/login');
    }
  }
}
```

**Переваги:**

- Повторне використання в усіх тестах.
- Тести не знають про селектори — тільки про методи типу `login()`, `verifySuccessfulLogin()`.

---

## 3. Тести (`e2e/*.spec.ts`)

Спеки створюють Page Objects і викликають їхні методи. Конфіг беруть із `fixtures/env.ts` (`testConfig`).

```typescript
// e2e/login.spec.ts
import { test } from '@playwright/test';
import { testConfig } from '../fixtures/env';
import { LoginPage } from '../pages/LoginPage';

test('успішний логін з валідними даними', async ({ page }) => {
  const { loginUrl, userEmail, userPassword, dashboardUrl } = testConfig;
  const loginPage = new LoginPage(page);
  await loginPage.navigateToLogin(loginUrl);
  await loginPage.login(userEmail!, userPassword!);
  await loginPage.verifySuccessfulLogin(dashboardUrl ?? undefined);
});
```

---

## Як додати нову сторінку

### Крок 1: Локатори

Створити файл `locators/your-page.locators.ts`:

```typescript
export const yourPageLocators = {
  mainButton: "role=button[name='Зберегти']",
  inputField: '#your-input',
} as const;
```

### Крок 2: Page Object

Створити файл `pages/YourPage.ts`:

```typescript
import { BasePage } from './BasePage';
import { yourPageLocators } from '../locators/your-page.locators';

export class YourPage extends BasePage {
  async doAction(): Promise<void> {
    await this.page.locator(yourPageLocators.mainButton).click();
    await this.waitForLoadState('networkidle');
  }
}
```

### Крок 3: Використання в тестах

У `e2e/*.spec.ts`:

```typescript
import { YourPage } from '../pages/YourPage';

test('щось робить на новій сторінці', async ({ page }) => {
  const yourPage = new YourPage(page);
  await yourPage.goto('https://...');
  await yourPage.doAction();
});
```

---

## Оновлення локаторів

Якщо змінився селектор на продукті:

1. Відкрити відповідний файл у `locators/`.
2. Змінити значення потрібного ключа.
3. Усі Page Objects і тести, що використовують цей локатор, отримають оновлення автоматично.

---

## Кросс-браузерне тестування

Playwright підтримує Chromium, Firefox, WebKit. Page Objects використовують стандартні Playwright API, тому один і той самий код працює у всіх браузерах.

**Запуск:**

```bash
cd tests-ts
# За замовчуванням — Chromium
npm run test

# Конкретний браузер
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit

# З відкритим вікном
npm run test:headed
```

Налаштування проєктів — у `playwright.config.ts`.

---

## Best practices

1. **Один Page Object — одна сторінка (або один логічний екран).**
2. **Локатори тільки в `locators/`** — у spec-файлах і Page Objects не хардкодити селектори.
3. **Базовий клас** — загальні методи (`goto`, `getUrl`, `waitForLoadState`) в `BasePage`.
4. **Описові назви методів** — `fillEmail`, `verifySuccessfulLogin`, `clickSaveButton`.
5. **Перевірки в Page Object або в тесті** — дрібні перевірки (наприклад, `isErrorMessageVisible`) можна в PO; складні сценарії залишати в spec з `expect()`.
6. **Конфіг і секрети** — тільки через `fixtures/env.ts` та `.env`, без хардкоду в тестах.

---

## Приклади з проєкту

| Сторінка / область   | Локатори                  | Page Object   | Спеки                |
|----------------------|---------------------------|---------------|-----------------------|
| Логін                | `login.locators.ts`       | `LoginPage`   | `login.spec.ts`       |
| XML-фіди та мапінг   | `xml-feed.locators.ts`    | `XmlFeedPage` | `xml-feed.spec.ts`, `excel-mapping.spec.ts` |

Excel-мапінг не має окремого Page Object — це той самий екран редагування фіду, тому методи типу `downloadExcelMappingFile` та `uploadExcelMappingFile` знаходяться в `XmlFeedPage`.

---

**Див. також:** [README.md](README.md) (індекс документації), [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) (структура tests-ts).

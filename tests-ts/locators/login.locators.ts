/**
 * Локатори сторінки логіну (відповідають tests-Python/locators/login_locators.py).
 * Додано варіанти для помилки валідації Ant Design (різні версії/структури).
 */
export const loginLocators = {
  emailInput: '#email',
  passwordInput: '#password',
  loginButton: "role=button[name='Увійти']",
  errorAlert: 'form .ant-alert.ant-alert-error',
  /** Помилка валідації під полем — Ant Design */
  fieldValidationError: 'form .ant-form-item-explain-error',
  /** Контейнер пояснення (текст помилки може бути всередині) */
  fieldValidationExplain: 'form .ant-form-item-explain',
  /** Будь-який елемент з класом explain (Ant Design v4/v5) */
  fieldValidationAny: '[class*="ant-form-item-explain"]',
} as const;

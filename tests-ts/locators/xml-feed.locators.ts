/**
 * Локатори сторінки XML-фідів (відповідають tests-Python/locators/xml_feed_locators.py).
 */
export const xmlFeedLocators = {
  productsMenu: 'text=Товари',
  importNewItemsLink: "role=link[name='Імпорт новинок']",
  xmlTabLink: "role=link[name='XML']",
  userMenu: 'text=Ilona / Ілона Karpenko',
  allSuppliersOption: 'text=Всі (8859)',
  suppliersSearchInput: "[placeholder*='Постачальник']",
  addNewFeedButton: "role=button[name='Додати новий фід']",
  saveButton: "role=button[name='Зберегти']",
  feedUrlInput: "input[placeholder*='fmt']",
  successMessage: 'text=Дані збережено!',
  feedLinkColumnHeader: 'text=Лінк фіду',
  connectedColumnHeader: 'text=Підключено?',
  feedLinkFilterIcon:
    'div:nth-child(4) > .ag-header-cell-comp-wrapper > .ag-cell-label-container > .ag-header-icon > .ag-icon',
  lastUploadColumnHeader: 'text=Останнє завантаження',
  managementButton: 'text=Управління',
  editButton: "button:has-text('Редагувати')",
  downloadExcelMappingButton: 'text=Отримати файл для ручного мапінгу',
  uploadExcelMappingButton: 'text=Завантажити ручний мапінг категорій',
} as const;

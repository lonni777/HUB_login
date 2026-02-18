/**
 * Конфігурація тестів з .env (завантажується в playwright.config.ts з кореня репозиторію).
 */
const baseUrl = process.env.TEST_BASE_URL || 'https://hubtest.kasta.ua';
const loginUrl = process.env.TEST_LOGIN_URL || `${baseUrl}/user/login`;

export const testConfig = {
  baseUrl,
  loginUrl,
  userEmail: process.env.TEST_USER_EMAIL || '',
  userPassword: process.env.TEST_USER_PASSWORD || '',
  dashboardUrl: process.env.TEST_DASHBOARD_URL || '',
  nonExistentUserEmail: process.env.TEST_NON_EXISTENT_USER_EMAIL || '',

  // XML-фіди
  xmlFeedsUrl: process.env.TEST_XML_FEEDS_URL || `${baseUrl}/supplier-content/xml`,
  testXmlFeedUrl:
    process.env.TEST_XML_FEED_URL ||
    'https://gist.githubusercontent.com/lonni777/dc7d69b7226ce29d807d762bbb054598/raw',
  testInvalidXmlFeedUrl:
    process.env.TEST_INVALID_XML_FEED_URL ||
    'https://www.dropbox.com/scl/fi/o84mvoxjl0ro6iejsh60p/Untitled-1.xml?rlkey=p09wc82oxv8rfl5c4pho4bfin&st=8k4hz546&dl=1',
  test404FeedUrl:
    process.env.TEST_404_FEED_URL ||
    'https://gist.github.com/lonni777/1eb5d08a1dfd4ad0fdf8666ab78ab5be111/raw',
  testInvalidUrlFeed: process.env.TEST_INVALID_URL_FEED || 'ftp://test.com',
  testInvalidXmlStructureUrl:
    process.env.TEST_INVALID_XML_STRUCTURE_URL ||
    'https://gist.githubusercontent.com/lonni777/231bc3625b32b6d8ae95374f154a4e30/raw',
  testTimeoutFeedUrl: process.env.TEST_TIMEOUT_FEED_URL || 'http://192.0.2.1/xml',
  testSupplierName: process.env.TEST_SUPPLIER_NAME || 'Парфюмс',
  testDuplicateFeedUrl:
    process.env.TEST_DUPLICATE_FEED_URL || 'https://www.foxtrot.com.ua/pricelist/kasta_uk.xml',
  testExistingFeedId: process.env.TEST_EXISTING_FEED_ID || 'R3DV',
  testFeedIdsForLimit: (process.env.TEST_FEED_IDS_FOR_LIMIT || 'R3DV,R2K3,R3DX,R3DY')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean),

  // БД (для cleanup; як у Python — TEST_DB_* з .env)
  dbHost: process.env.TEST_DB_HOST || '',
  dbPort: parseInt(process.env.TEST_DB_PORT || '5432', 10),
  dbName: process.env.TEST_DB_NAME || '',
  dbUser: process.env.TEST_DB_USER || '',
  dbPassword: process.env.TEST_DB_PASSWORD || '',
  /** Увімкнути SSL (require), якщо сервер вимагає шифрування (pg_hba.conf). Значення: '1', 'true', 'require' */
  dbSsl: process.env.TEST_DB_SSL || '',
} as const;

export type TestConfig = typeof testConfig;

/**
 * HTTP-сервер для тесту «вимкнення фіда блокує нові завантаження».
 * Один URL /feed.xml: 1-й запит повертає XML з 1 товаром, 2-й — з 2 товарами.
 * Порт за замовчуванням 9877. Hub (бекенд) має мати доступ до цього URL.
 *
 * Використання: node scripts/serve-http-feed-two-versions.js [port]
 */
const http = require('http');

const PORT = parseInt(process.argv[2] || '9877', 10);

const XML_ONE_ITEM = `<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item>
    <title>Item for disabled-feed test</title>
    <id>blocked-test-1</id>
    <price>100</price>
  </item>
</items>`;

const XML_TWO_ITEMS = `<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item>
    <title>Item for disabled-feed test</title>
    <id>blocked-test-1</id>
    <price>100</price>
  </item>
  <item>
    <title>New item that must not be loaded when checkbox is off</title>
    <id>blocked-test-2</id>
    <price>200</price>
  </item>
</items>`;

let requestCount = 0;

const server = http.createServer((req, res) => {
  if (req.url === '/feed.xml' || req.url === '/' || req.url === '') {
    requestCount += 1;
    const body = requestCount === 1 ? XML_ONE_ITEM : XML_TWO_ITEMS;
    res.writeHead(200, {
      'Content-Type': 'application/xml',
      'Access-Control-Allow-Origin': '*',
    });
    res.end(body);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`Two-version feed: http://localhost:${PORT}/feed.xml (1st req=1 item, 2nd+=2 items)`);
});

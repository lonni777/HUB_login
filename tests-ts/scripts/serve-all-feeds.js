/**
 * Запускає обидва mock-сервери фідів в одному процессі:
 * - 9876: фід для тесту «збереження фіду з http» (serve-http-feed)
 * - 9877: фід з двома варіантами для тесту «вимкнення фіда блокує нові завантаження»
 *
 * Використання: node scripts/serve-all-feeds.js
 * Playwright webServer використовує цей скрипт, щоб обидва тести мали доступ до моків.
 */
const http = require('http');

const PORT1 = 9876;
const PORT2 = 9877;

const MINIMAL_XML = `<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item>
    <title>Test Product</title>
    <id>test-1</id>
    <price>100</price>
  </item>
</items>`;

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

let twoVersionRequestCount = 0;

const server1 = http.createServer((req, res) => {
  if (req.url === '/feed.xml' || req.url === '/' || req.url === '') {
    res.writeHead(200, { 'Content-Type': 'application/xml', 'Access-Control-Allow-Origin': '*' });
    res.end(MINIMAL_XML);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

const server2 = http.createServer((req, res) => {
  if (req.url === '/feed.xml' || req.url === '/' || req.url === '') {
    twoVersionRequestCount += 1;
    const body = twoVersionRequestCount === 1 ? XML_ONE_ITEM : XML_TWO_ITEMS;
    res.writeHead(200, { 'Content-Type': 'application/xml', 'Access-Control-Allow-Origin': '*' });
    res.end(body);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server1.listen(PORT1, '0.0.0.0', () => {
  console.log(`Feed 9876: http://localhost:${PORT1}/feed.xml`);
});
server2.listen(PORT2, '0.0.0.0', () => {
  console.log(`Feed 9877 (two versions): http://localhost:${PORT2}/feed.xml`);
});

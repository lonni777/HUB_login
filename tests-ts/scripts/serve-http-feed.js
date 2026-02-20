/**
 * Мінімальний HTTP-сервер для імітації XML-фіду з протоколом http://
 *
 * Використання:
 *   node scripts/serve-http-feed.js [port]
 *
 * За замовчуванням порт 9876. XML доступний за http://localhost:9876/feed.xml
 *
 * Обмеження: Hub-бекенд має доступити до цього URL.
 * - Якщо Hub локально (наприклад docker): використовуй host.docker.internal:9876
 * - Якщо Hub на hubtest.kasta.ua: потрібен публічний URL (тунель або окремий сервер)
 */
const http = require('http');

const PORT = parseInt(process.argv[2] || '9876', 10);

const MINIMAL_XML = `<?xml version="1.0" encoding="UTF-8"?>
<items>
  <item>
    <title>Test Product</title>
    <id>test-1</id>
    <price>100</price>
  </item>
</items>`;

const server = http.createServer((req, res) => {
  if (req.url === '/feed.xml' || req.url === '/' || req.url === '') {
    res.writeHead(200, {
      'Content-Type': 'application/xml',
      'Access-Control-Allow-Origin': '*',
    });
    res.end(MINIMAL_XML);
  } else {
    res.writeHead(404);
    res.end('Not found');
  }
});

server.listen(PORT, '0.0.0.0', () => {
  console.log(`HTTP feed server: http://localhost:${PORT}/feed.xml`);
  console.log(`For Hub in Docker: http://host.docker.internal:${PORT}/feed.xml`);
});

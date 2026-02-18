/**
 * Копіює поточний allure-report у reports/history/<suite>/run_<timestamp>
 * і залишає тільки останні 3 прогони для цього сьюту.
 * Запуск: node scripts/rotate-allure-history.js <suite>
 * suite: login | xml-feed | excel-mapping
 */
const fs = require('fs');
const path = require('path');

const KEEP_LAST = 3;
const reportsDir = path.join(__dirname, '..', '..', 'reports');
const allureReport = path.join(reportsDir, 'allure-report');
const suite = process.argv[2] || 'full';

if (!suite.match(/^[a-z0-9-]+$/)) {
  console.error('Suite name must be alphanumeric with hyphens (e.g. login, xml-feed, excel-mapping)');
  process.exit(1);
}

const historySuiteDir = path.join(reportsDir, 'history', suite);
const timestamp = new Date().toISOString().replace(/[-:T.Z]/g, '').slice(0, 14);
const runDir = path.join(historySuiteDir, `run_${timestamp}`);

if (!fs.existsSync(allureReport)) {
  console.error('reports/allure-report not found. Run allure generate first.');
  process.exit(1);
}

function copyDir(src, dest) {
  fs.mkdirSync(dest, { recursive: true });
  for (const name of fs.readdirSync(src)) {
    const srcPath = path.join(src, name);
    const destPath = path.join(dest, name);
    if (fs.statSync(srcPath).isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      fs.copyFileSync(srcPath, destPath);
    }
  }
}

try {
  fs.mkdirSync(historySuiteDir, { recursive: true });
  copyDir(allureReport, runDir);
  console.log(`Copied allure-report to ${runDir}`);
} catch (err) {
  console.error(err);
  process.exit(1);
}

const dirs = fs.readdirSync(historySuiteDir, { withFileTypes: true })
  .filter((d) => d.isDirectory() && d.name.startsWith('run_'))
  .map((d) => ({
    name: d.name,
    path: path.join(historySuiteDir, d.name),
    mtime: fs.statSync(path.join(historySuiteDir, d.name)).mtimeMs,
  }))
  .sort((a, b) => b.mtime - a.mtime);

for (let i = KEEP_LAST; i < dirs.length; i++) {
  try {
    fs.rmSync(dirs[i].path, { recursive: true });
    console.log(`Removed old run: ${dirs[i].name}`);
  } catch (e) {
    console.warn(e.message);
  }
}

console.log(`Kept last ${Math.min(KEEP_LAST, dirs.length)} run(s) for suite "${suite}".`);

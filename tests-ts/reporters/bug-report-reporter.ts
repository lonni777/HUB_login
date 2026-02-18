/**
 * Репортер для tests-ts: при падінні тесту записує reports/last_failure_bug_report.txt
 * у тому ж форматі, що й Python (pytest), щоб можна було взяти репорт для Jira.
 */
import fs from 'fs';
import path from 'path';
import type { Reporter, TestCase, TestResult } from '@playwright/test/reporter';

const DEFAULT_OPTIONS = {
  reportsDir: path.join(__dirname, '..', '..', 'reports'),
  currentReportFolder: 'playwright',
};

type Options = typeof DEFAULT_OPTIONS;

export default class BugReportReporter implements Reporter {
  private options: Options;
  private reportsDir: string;
  private reportFolder: string;

  constructor(options: Partial<Options> = {}) {
    this.options = { ...DEFAULT_OPTIONS, ...options };
    this.reportsDir = this.options.reportsDir;
    this.reportFolder = this.options.currentReportFolder;
  }

  printsToStdio(): boolean {
    return false;
  }

  onTestEnd(test: TestCase, result: TestResult): void {
    if (result.status !== 'failed') return;

    const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19);
    const testTitle = test.title;
    const testLocation = `${test.location.file}:${test.location.line}`;
    const errorMsg = result.error ? (result.error.message || String(result.error)) : 'Невідома помилка';
    const errorSnippet = errorMsg.slice(0, 1500);

    const attachments: string[] = [];
    if (result.attachments) {
      for (const att of result.attachments) {
        if (att.path) attachments.push(`${att.name || 'Вкладено'}: ${att.path}`);
      }
    }
    const htmlReportPath = path.join(this.reportsDir, this.reportFolder, 'index.html');
    if (fs.existsSync(path.join(this.reportsDir, this.reportFolder))) {
      attachments.push(`HTML звіт: ${htmlReportPath}`);
    }

    const content = `=== БАГ-РЕПОРТ ДЛЯ JIRA (копіювати вручну) ===
Згенеровано: ${timestamp}

--- Summary ---
[Автотест] ${testTitle}: ${errorMsg.slice(0, 80)}...

--- Description ---
**Тест:** ${testTitle}
**Файл:** ${testLocation}

**Помилка:**
${errorSnippet}

**Кроки для відтворення:** (див. тест-кейс)

**Очікуваний результат:** (з тест-кейсу)
**Фактичний результат:** (див. помилку вище)

**Середовище:** Node.js, Playwright (tests-ts)

--- Attachments ---
${attachments.length ? attachments.join('\n') : '(немає)'}
`;

    try {
      if (!fs.existsSync(this.reportsDir)) fs.mkdirSync(this.reportsDir, { recursive: true });
      const bugReportPath = path.join(this.reportsDir, 'last_failure_bug_report.txt');
      fs.writeFileSync(bugReportPath, content, 'utf-8');
      console.log(`\n>>> Bug report збережено: ${bugReportPath}`);
      console.log('>>> Можна створити issue в Jira, скопіювавши вміст файлу.\n');
    } catch (e) {
      console.error('Не вдалося зберегти bug report:', e);
    }
  }
}

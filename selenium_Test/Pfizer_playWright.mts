import { chromium } from 'playwright';
import * as fs from 'fs';

await fs.promises.mkdir('screenshots', { recursive: true });

const browser = await chromium.launch({ headless: false });
const context = await browser.newContext();
const page = await context.newPage();

const passed: string[] = [];
const failed: string[] = [];

const screenshot = async (name: string) => {
  await page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
};

const runTest = async (label: string, action: () => Promise<void>) => {
  try {
    await action();
    passed.push(label);
    console.log(`✅ ${label}`);
  } catch (error) {
    failed.push(label);
    if (error instanceof Error) {
      console.error(`❌ ${label} - ${error.message}`);
    } else {
      console.error(`❌ ${label} - Unknown error`, error);
    }
  }
};

await page.goto('https://www.pfizerforall.com/');
await page.waitForLoadState('networkidle');
await screenshot('homepage');
console.log('[✓] Homepage loaded');

// === CTA Sections ===
const ctas = [
  'Manage migraine',
  'Navigate menopause',
  'Schedule vaccines',
  'Save on Pfizer medications',
  'Get answers to health and wellness questions',
  'COVID‑19, flu, or just a cold? Let’s find out.',
  'Take health questionnaires'
];

for (const text of ctas) {
  await runTest(`Navigate to: ${text}`, async () => {
    await page.goto('https://www.pfizerforall.com/');
    const locator = page.locator(`text=${text}`);
    await locator.first().scrollIntoViewIfNeeded();
    await locator.first().waitFor({ state: 'visible', timeout: 5000 });
    const box = await locator.first().boundingBox();
    if (!box) throw new Error(`Could not find bounding box for: ${text}`);
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForLoadState('networkidle');
    await screenshot(text.toLowerCase().replace(/\W+/g, '_'));
  });
}

// === Ask a Question Tool ===
await runTest('Open Health Answers tool', async () => {
  await page.goto('https://www.pfizerforall.com/');
  const askButton = await page.waitForSelector('text="Ask a question"', { timeout: 5000 });
  const [healthAnswers] = await Promise.all([
    context.waitForEvent('page'),
    askButton.click()
  ]);
  await healthAnswers.waitForLoadState();
  await healthAnswers.screenshot({ path: 'screenshots/health_answers.png', fullPage: true });
  await healthAnswers.close();
});

// === “Get Started” Buttons ===
await runTest('Click each Get started button', async () => {
  await page.goto('https://www.pfizerforall.com/');
  const buttons = await page.locator('text=Get started').elementHandles();
  for (let i = 0; i < buttons.length; i++) {
    await page.goto('https://www.pfizerforall.com/');
    const refreshed = await page.locator('text=Get started').elementHandles();
    const handle = refreshed[i];
    const box = await handle.boundingBox();
    if (!box) throw new Error(`No bounding box for Get started #${i + 1}`);
    await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
    await page.waitForLoadState();
    await screenshot(`get_started_${i + 1}`);
  }
});

// === Sign-Up Form ===
await runTest('Fill and submit sign-up form', async () => {
  await page.goto('https://www.pfizerforall.com/sign-up');
  await page.waitForLoadState('networkidle');
  await page.fill('input[name="firstName"]', 'Jane');
  await page.fill('input[name="lastName"]', 'Doe');
  await page.fill('input[name="email"]', 'jane.doe@example.com');
  await page.click('button[type="submit"]');
  await page.waitForTimeout(2000);
  await screenshot('signup_complete');
});

// === Final Test Summary ===
console.log('\n===== TEST SUMMARY =====');
console.log(`✅ Passed: ${passed.length}`);
passed.forEach(t => console.log(`  - ${t}`));
console.log(`❌ Failed: ${failed.length}`);
failed.forEach(t => console.log(`  - ${t}`));

await browser.close();
console.log('[✓] Browser closed');
console.log('[✓] All tests completed');
console.log('[✓] Screenshots saved in the screenshots folder');
console.log('[✓] Test script finished');
console.log('[✓] Please check the console for any errors or failed tests.');

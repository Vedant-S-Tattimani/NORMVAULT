const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const ARTIFACTS_DIR = 'C:/Users/Lenovo/.gemini/antigravity-ide/brain/dc1bf6b2-4892-42aa-ac84-18350561f17e';

async function run() {
  let browser;
  try {
    browser = await chromium.launch({ channel: 'chrome', headless: true });
  } catch (e) {
    browser = await chromium.launch({ channel: 'msedge', headless: true });
  }
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 }
  });
  const page = await context.newPage();

  console.log('1. Navigating to http://localhost:5173/');
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle', timeout: 15000 });
  await page.waitForTimeout(1000);

  // Take screenshot of English homepage
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '01_homepage_en.png'), fullPage: false });
  console.log('Saved 01_homepage_en.png');

  // Find the top-left language switcher
  console.log('2. Opening Language Switcher modal...');
  const langBtn = page.locator('button[title*="Switch language"], button:has-text("English"), button:has-text("🌐")').first();
  await langBtn.click();
  await page.waitForTimeout(500);

  // Take screenshot of Language Modal showing 20 Indian languages
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '02_language_modal.png'), fullPage: false });
  console.log('Saved 02_language_modal.png');

  // Select Hindi (हिन्दी)
  console.log('3. Selecting Hindi language...');
  const hindiBtn = page.locator('button:has-text("हिन्दी")').first();
  await hindiBtn.click();
  await page.waitForTimeout(1000);

  // Take screenshot of translated Hindi homepage
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '03_homepage_hindi.png'), fullPage: false });
  console.log('Saved 03_homepage_hindi.png');

  // Verify Hindi texts
  const heroTitle = await page.locator('h1').first().textContent();
  console.log('Hindi Hero Title:', heroTitle);

  // Navigate to Standards page
  console.log('4. Navigating to Standards Catalog in Hindi...');
  const standardsNav = page.locator('header nav button:has-text("मानक"), header nav button:has-text("मानक सूची")').first();
  if (await standardsNav.count() > 0) {
    await standardsNav.click();
  } else {
    // Click category chip
    await page.locator('button:has-text("इलेक्ट्रो-तकनीकी"), button:has-text("खाद्य एवं कृषि")').first().click();
  }
  await page.waitForTimeout(1500);

  // Take screenshot of Hindi Standards page
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '04_standards_hindi.png'), fullPage: false });
  console.log('Saved 04_standards_hindi.png');

  // Switch to Telugu (తెలుగు)
  console.log('5. Switching to Telugu...');
  const topLangBtn = page.locator('header button:has-text("🌐"), button[title*="भाषा"], button[title*="Language"]').first();
  await topLangBtn.click();
  await page.waitForTimeout(500);

  const teluguBtn = page.locator('button:has-text("తెలుగు")').first();
  await teluguBtn.click();
  await page.waitForTimeout(1000);

  // Take screenshot of Telugu Standards page
  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '05_standards_telugu.png'), fullPage: false });
  console.log('Saved 05_standards_telugu.png');

  // Test mobile viewport
  console.log('6. Testing mobile responsive view with language switcher...');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);

  await page.screenshot({ path: path.join(ARTIFACTS_DIR, '06_mobile_multilingual.png'), fullPage: false });
  console.log('Saved 06_mobile_multilingual.png');

  await browser.close();
  console.log('Multilingual i18n testing completed successfully!');
}

run().catch((err) => {
  console.error('Test failed:', err);
  process.exit(1);
});

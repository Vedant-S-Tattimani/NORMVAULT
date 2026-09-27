const { chromium } = require('playwright');
const path = require('path');

async function testKannada() {
  console.log('🔍 Testing Kannada (kn) translation and visual rendering...');
  const browser = await chromium.launch({ headless: true, channel: 'chrome' });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();

  let errorCount = 0;
  page.on('pageerror', err => {
    console.error('❌ Page Error:', err.message);
    errorCount++;
  });

  await page.goto('http://localhost:5173', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);

  // Switch to Kannada via window.changeAppLanguage
  await page.evaluate(() => {
    if (window.changeAppLanguage) {
      window.changeAppLanguage('kn');
    }
  });

  await page.waitForTimeout(800);

  // Verify Kannada elements
  const bodyText = await page.innerText('body');

  const tests = [
    { name: 'Hero Headline', text: 'ಮಾನದಂಡಗಳವರೆಗೆ', found: bodyText.includes('ಮಾನದಂಡಗಳವರೆಗೆ') },
    { name: 'Ecosystem Kicker', text: 'ಸಂಸ್ಥಾಗತ ವಿಶ್ವಾಸಾರ್ಹತೆ', found: bodyText.includes('ಸಂಸ್ಥಾಗತ ವಿಶ್ವಾಸಾರ್ಹತೆ') },
    { name: 'Ecosystem Title', text: 'ಭಾರತದ ಸಾರ್ವಜನಿಕ ಖರೀದಿ ಪರಿಸರ', found: bodyText.includes('ಭಾರತದ ಸಾರ್ವಜನಿಕ ಖರೀದಿ ಪರಿಸರ') },
    { name: 'Ecosystem BIS Act', text: 'BIS ಕಾಯ್ದೆ 2016', found: bodyText.includes('BIS ಕಾಯ್ದೆ 2016') },
    { name: 'Problem Pitfalls', text: 'ಸಾಂಪ್ರದಾಯಿಕ ಖರೀದಿ ತೊಡಕುಗಳು', found: bodyText.includes('ಸಾಂಪ್ರದಾಯಿಕ ಖರೀದಿ ತೊಡಕುಗಳು') },
    { name: 'Workflow 7-Stages', text: '7-ಹಂತದ ಖರೀದಿ ಬುದ್ಧಿಮತ್ತೆ ಪೈಪ್‌ಲೈನ್', found: bodyText.includes('7-ಹಂತದ ಖರೀದಿ ಬುದ್ಧಿಮತ್ತೆ ಪೈಪ್‌ಲೈನ್') },
    { name: 'Stakeholder Capabilities', text: 'ಸಾರ್ವಜನಿಕ ಖರೀದಿಯ ಪ್ರತಿಯೊಬ್ಬ ಪಾಲುದಾರರಿಗಾಗಿ', found: bodyText.includes('ಸಾರ್ವಜನಿಕ ಖರೀದಿಯ ಪ್ರತಿಯೊಬ್ಬ ಪಾಲುದಾರರಿಗಾಗಿ') },
    { name: 'Impact Metrics', text: 'ಅಳೆಯಬಹುದಾದ ಖರೀದಿ ಪ್ರಭಾವ', found: bodyText.includes('ಅಳೆಯಬಹುದಾದ ಖರೀದಿ ಪ್ರಭಾವ') },
    { name: 'Institutional CTA', text: 'ನಿಮ್ಮ ಮುಂದಿನ ಟೆಂಡರ್‌ನಿಂದ', found: bodyText.includes('ನಿಮ್ಮ ಮುಂದಿನ ಟೆಂಡರ್‌ನಿಂದ') },
    { name: 'Footer Text', text: 'ಎಲ್ಲಾ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ', found: bodyText.includes('ಎಲ್ಲಾ ಹಕ್ಕುಗಳನ್ನು ಕಾಯ್ದಿರಿಸಲಾಗಿದೆ') }
  ];

  console.log('\nResults for Kannada (kn):');
  let allPassed = true;
  for (const t of tests) {
    console.log(`  ${t.found ? '✅' : '❌'} ${t.name}: "${t.text}" -> ${t.found ? 'FOUND' : 'MISSING'}`);
    if (!t.found) allPassed = false;
  }

  // Check that NO Hindi text is present in EcosystemBanner or ProblemSection
  const hindiCheck = bodyText.includes('भारत के सार्वजनिक खरीद') || bodyText.includes('संस्थागत विश्वास एवं वैधानिक अनुपालन');
  console.log(`  ${!hindiCheck ? '✅' : '❌'} Devanagari Hindi Leak Check: ${!hindiCheck ? 'CLEAN (NO HINDI DETECTED)' : 'LEAK DETECTED!'}`);
  if (hindiCheck) allPassed = false;

  // Capture Screenshot of Kannada home page
  const screenshotPath = path.resolve('C:/Users/Lenovo/.gemini/antigravity-ide/brain/dc1bf6b2-4892-42aa-ac84-18350561f17e/kannada_homepage_verified.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  console.log(`📸 Screenshot saved: ${screenshotPath}`);

  await browser.close();
  console.log('\nFinal Verdict:', allPassed && errorCount === 0 ? '🎉 ALL KANNADA TESTS PASSED!' : '❌ FAILURES ENCOUNTERED');
  process.exit(allPassed && errorCount === 0 ? 0 : 1);
}

testKannada().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});

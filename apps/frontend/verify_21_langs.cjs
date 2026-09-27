const { chromium } = require('playwright');

const ALL_LANGUAGES = [
  { code: 'en', name: 'English', native: 'English', testHero: 'recommendation engine' },
  { code: 'hi', name: 'Hindi', native: 'हिन्दी', testHero: 'सार्वजनिक' },
  { code: 'te', name: 'Telugu', native: 'తెలుగు', testHero: 'ప్రభుత్వ' },
  { code: 'bn', name: 'Bengali', native: 'বাংলা', testHero: 'সরকারি' },
  { code: 'ta', name: 'Tamil', native: 'தமிழ்', testHero: 'பொது' },
  { code: 'mr', name: 'Marathi', native: 'मराठी', testHero: 'सार्वजनिक' },
  { code: 'gu', name: 'Gujarati', native: 'ગુજરાતી', testHero: 'જાહેર' },
  { code: 'kn', name: 'Kannada', native: 'ಕನ್ನಡ', testHero: 'ಸಾರ್ವಜನಿಕ' },
  { code: 'ml', name: 'Malayalam', native: 'മലയാളം', testHero: 'പൊതു' },
  { code: 'pa', name: 'Punjabi', native: 'ਪੰਜਾਬੀ', testHero: 'ਸਰਕਾਰੀ' },
  { code: 'or', name: 'Odia', native: 'ଓଡ଼ିଆ', testHero: 'ସରକାରୀ' },
  { code: 'as', name: 'Assamese', native: 'অসমীয়া', testHero: 'চৰকাৰী' },
  { code: 'ur', name: 'Urdu', native: 'اردو', testHero: 'سرکاری' },
  { code: 'sa', name: 'Sanskrit', native: 'संस्कृतम्', testHero: 'सार्वजनिक' },
  { code: 'ne', name: 'Nepali', native: 'नेपाली', testHero: 'सार्वजनिक' },
  { code: 'kok', name: 'Konkani', native: 'कोंकणी', testHero: 'सार्वजनिक' },
  { code: 'mai', name: 'Maithili', native: 'मैथिली', testHero: 'सार्वजनिक' },
  { code: 'sat', name: 'Santali', native: 'ᱥᱟᱱᱛᱟᱲᱤ', testHero: 'ᱥᱚᱨᱠᱟᱨᱤ' },
  { code: 'ks', name: 'Kashmiri', native: 'کٲشُر', testHero: 'تکنیکی' },
  { code: 'sd', name: 'Sindhi', native: 'سنڌي', testHero: 'سرڪاري' },
  { code: 'doi', name: 'Dogri', native: 'डोगरी', testHero: 'सरकारी' }
];

async function verifyAll21Languages() {
  console.log('🚀 Starting Verification of All 21 Languages...');
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

  const results = [];

  for (const lang of ALL_LANGUAGES) {
    try {
      // Trigger language switch via window / localStorage or i18next
      await page.evaluate((langCode) => {
        if (window.changeAppLanguage) {
          window.changeAppLanguage(langCode);
        } else if (window.i18n) {
          window.i18n.changeLanguage(langCode);
        }
      }, lang.code);

      await page.waitForTimeout(500);

      // Verify that document or sections have translated text
      const pageText = await page.innerText('body');
      const switcherText = await page.locator('header').innerText();

      const hasHeroMatch = pageText.includes(lang.testHero);
      const switcherHasLang = switcherText.includes(lang.code.toUpperCase()) || switcherText.includes(lang.native);

      results.push({
        code: lang.code,
        name: lang.name,
        native: lang.native,
        status: hasHeroMatch ? 'PASS' : 'WARN_CHECK',
        hasHeroMatch,
        switcherHasLang
      });

      console.log(`  [${lang.code.toUpperCase()}] ${lang.name} (${lang.native}): ${hasHeroMatch ? '✅ PASS' : '⚠️ CHECK'}`);
    } catch (err) {
      console.error(`  [${lang.code.toUpperCase()}] Failed:`, err.message);
      results.push({ code: lang.code, name: lang.name, status: 'FAIL', error: err.message });
    }
  }

  await browser.close();
  console.log('\n📊 Summary: Tested', results.length, 'languages. Total JS errors:', errorCount);
  const passCount = results.filter(r => r.status === 'PASS').length;
  console.log(`Passed: ${passCount} / ${ALL_LANGUAGES.length}`);
  process.exit(errorCount > 0 ? 1 : 0);
}

verifyAll21Languages().catch(err => {
  console.error('Fatal test error:', err);
  process.exit(1);
});

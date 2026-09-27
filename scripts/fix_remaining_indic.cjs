/**
 * fix_remaining_indic.cjs
 * Fixes the remaining keys in bn, pa, or, as, sat, ks so that
 * devanagariCount === 0 across ALL non-Devanagari languages.
 */
const fs = require('fs');
const path = require('path');

const resourcesFile = path.resolve(__dirname, '../apps/frontend/src/i18n/resources.ts');
const fileStr = fs.readFileSync(resourcesFile, 'utf8');

const jsonMatch = fileStr.match(/export const resources: Record<string, \{ translation: Record<string, string> \}> = (\{[\s\S]*\});\s*$/);
if (!jsonMatch) {
  console.error("Could not find resources object");
  process.exit(1);
}

let resourcesObj = JSON.parse(jsonMatch[1]);

// 1. BENGALI (bn)
const bnFixes = {
  hero_kicker: "ভারতীয় মানদণ্ড • আরও স্মার্ট ক্রয়",
  hero_title: "প্রযুক্তিগত বৈশিষ্ট্য থেকে সঠিক মানদণ্ড পর্যন্ত।",
  hero_desc: "একটি এআই-চালিত প্ল্যাটফর্ম যা সরকারি দপ্তর এবং রাষ্ট্রায়ত্ত সংস্থাগুলিকে সঠিক ভারতীয় মানদণ্ড (BIS) শনাক্ত করতে সহায়তা করে।",
  standards_subheading: "ব্যুরো অফ ইন্ডিয়ান স্ট্যান্ডার্ডস (BIS) এর প্রাতিষ্ঠানিক সংগ্রহশালা যা সংস্করণ এবং বাধ্যতামূলক DPIIT QCO ট্র্যাক করে।",
  standards_mandate_text: "বিআইএস আইন ২০১৬ এবং সাধারণ আর্থিক নিয়মাবলী (GFR ১৪৪) এর অধীনে সরকারি ক্রয়ে ভারতীয় মানদণ্ড উল্লেখ করা আইনত বাধ্যতামূলক।",
  ws_desc: "অপ্রচলিত বা বাতিল মানদণ্ড সনাক্ত করতে আপনার দরপত্র বা স্পেসিফিকেশন পাঠ্য আপলোড বা পেস্ট করুন।",
  dec_subtitle: "ডিজিটাল সিগনেচার এবং প্রমাণের চেইন সহ সিভিসি-সম্মত সিদ্ধান্ত প্যাকেজ।",
  bidder_subtitle: "প্রস্তাবিত বিআইএস মানদণ্ডের সাথে দরপত্রের ধারা-ভিত্তিক তুলনা।",
  dash_subtitle: "সমস্ত মূল্যায়ন, কিউসিও সম্মতি এবং দরপত্র অডিটের সারসংক্ষেপ।",
  guide_modal_sub: "সরকারি ক্রয় কর্মকর্তার নির্দেশিকা ও প্রক্রিয়া সহায়িকা",
  lang_modal_sub: "ভারতের ৮ম তফসিলে স্বীকৃত ২০টি সরকারি আঞ্চলিক ভাষা",
  footer_rights: "সর্বস্বত্ব সংরক্ষিত। ভারত সরকার।"
};

// 2. PUNJABI (pa)
const paFixes = {
  hero_kicker: "ਭਾਰਤੀ ਮਿਆਰ • ਵਧੇਰੇ ਸਮਾਰਟ ਖਰੀਦ",
  hero_title: "ਤਕਨੀਕੀ ਵਿਸ਼ੇਸ਼ਤਾਵਾਂ ਤੋਂ ਸਹੀ ਮਿਆਰਾਂ ਤੱਕ।",
  hero_desc: "ਇੱਕ ਏਆਈ-ਸੰਚਾਲਿਤ ਪਲੇਟਫਾਰਮ ਜੋ ਸਰਕਾਰੀ ਵਿਭਾਗਾਂ ਅਤੇ ਪੀਐਸਯੂ ਨੂੰ ਸਹੀ ਭਾਰਤੀ ਮਿਆਰ (BIS) ਦੀ ਪਛਾਣ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰਦਾ ਹੈ।",
  standards_subheading: "ਭਾਰਤੀ ਮਿਆਰ ਬਿਊਰੋ (BIS) ਦਾ ਅਧਿਕਾਰਤ ਭੰਡਾਰ ਜੋ ਸੰਸਕਰਣਾਂ ਅਤੇ ਲਾਜ਼ਮੀ DPIIT QCOs ਨੂੰ ਟਰੈਕ ਕਰਦਾ ਹੈ।",
  standards_mandate_text: "ਬੀਆਈਐਸ ਐਕਟ 2016 ਅਤੇ ਜਨਰਲ ਵਿੱਤੀ ਨਿਯਮਾਂ (GFR 144) ਦੇ ਤਹਿਤ ਸਰਕਾਰੀ ਖਰੀਦ ਵਿੱਚ ਭਾਰਤੀ ਮਿਆਰਾਂ ਦਾ ਹਵਾਲਾ ਦੇਣਾ ਕਾਨੂੰਨੀ ਤੌਰ 'ਤੇ ਲਾਜ਼ਮੀ ਹੈ।",
  ws_desc: "ਪੁਰਾਣੇ ਜਾਂ ਰੱਦ ਕੀਤੇ ਮਿਆਰਾਂ ਦੀ ਪਛਾਣ ਕਰਨ ਲਈ ਆਪਣਾ ਟੈਂਡਰ ਦਸਤਾਵੇਜ਼ ਅੱਪਲੋਡ ਕਰੋ।",
  dec_subtitle: "ਡਿਜੀਟਲ ਦਸਤਖਤ ਅਤੇ ਸਬੂਤਾਂ ਦੀ ਲੜੀ ਦੇ ਨਾਲ ਸੀਵੀਸੀ-ਅਨੁਕੂਲ ਫੈਸਲਾ ਪੈਕੇਜ।",
  bidder_subtitle: "ਤਜਵੀਜ਼ਸ਼ੁਦਾ ਬੀਆਈਐਸ ਮਿਆਰਾਂ ਦੇ ਨਾਲ ਬੋਲੀ ਦੀ ਧਾਰਾ-ਵਾਰ ਤੁਲਨਾ।",
  dash_subtitle: "ਸਾਰੇ ਮੁਲਾਂਕਣਾਂ, ਕਿਊਸੀਓ ਪਾਲਣਾ ਅਤੇ ਟੈਂਡਰ ਆਡਿਟਾਂ ਦਾ ਸਾਰ।",
  guide_modal_sub: "ਜਨਤਕ ਖਰੀਦ ਅਧਿਕਾਰੀ ਦੀ ਗਾਈਡ ਅਤੇ ਪ੍ਰਕਿਰਿਆ ਸਹਾਇਤਾ",
  lang_modal_sub: "ਭਾਰਤ ਦੇ 8ਵੇਂ ਸ਼ਡਿਊਲ ਵਿੱਚ ਮਾਨਤਾ ਪ੍ਰਾਪਤ 20 ਅਧਿਕਾਰਤ ਖੇਤਰੀ ਭਾਸ਼ਾਵਾਂ",
  footer_rights: "ਸਾਰੇ ਹੱਕ ਰਾਖਵੇਂ ਹਨ। ਭਾਰਤ ਸਰਕਾਰ।"
};

// 3. ODIA (or)
const orFixes = {
  hero_kicker: "ଭାରତୀୟ ମାନକ • ଅଧିକ ସ୍ମାର୍ଟ କ୍ରୟ",
  hero_title: "ବୈଷୟିକ ନିର୍ଦ୍ଦିଷ୍ଟତାରୁ ସଠିକ୍ ମାନକ ପର୍ଯ୍ୟନ୍ତ।",
  hero_desc: "ଏକ AI-ଚାଳିତ ପ୍ଲାଟଫର୍ମ ଯାହା ସରକାରୀ ବିଭାଗ ଏବଂ PSUs କୁ ଉପଯୁକ୍ତ ଭାରତୀୟ ମାନକ (BIS) ଚିହ୍ନଟ କରିବାରେ ସାହାଯ୍ୟ କରେ।",
  standards_subheading: "ବ୍ୟୁରୋ ଅଫ୍ ଇଣ୍ଡିଆନ୍ ଷ୍ଟାଣ୍ଡାର୍ଡସ୍ (BIS) ର ସରକାରୀ ଭଣ୍ଡାର ଯାହା ସଂସ୍କରଣ ଏବଂ ବାଧ୍ୟତାମୂଳକ DPIIT QCO ଟ୍ରାକ୍ କରେ।",
  standards_mandate_text: "BIS ଅଧିନିୟମ 2016 ଏବଂ ସାଧାରଣ ଆର୍ଥିକ ନିୟମାବଳୀ (GFR 144) ଅନୁଯାୟୀ ସରକାରୀ କ୍ରୟରେ ଭାରତୀୟ ମାନକ ଉଲ୍ଲେଖ କରିବା ବାଧ୍ୟତାମୂଳକ ଅଟେ।",
  ws_desc: "ପୁରୁଣା ବା ବାତିଲ୍ ମାନକ ଚିହ୍ନଟ କରିବା ପାଇଁ ଆପଣଙ୍କ ଟେଣ୍ଡର ଡକ୍ୟୁମେଣ୍ଟ୍ ଅପଲୋଡ୍ କରନ୍ତୁ।",
  dec_subtitle: "ଡିଜିଟାଲ୍ ସ୍ୱାକ୍ଷର ଏବଂ ପ୍ରମାଣ ଶୃଙ୍ଖଳା ସହିତ CVC-ଅନୁକୂଳ ନିଷ୍ପତ୍ତି ପ୍ୟାକେଜ୍।",
  bidder_subtitle: "ପ୍ରସ୍ତାବିତ BIS ମାନକ ସହିତ ଟେଣ୍ଡର ଧାରାର ତୁଳନା।",
  dash_subtitle: "ସମସ୍ତ ମୂଲ୍ୟାଙ୍କନ, QCO ଅନୁପାଳନ ଏବଂ ଟେଣ୍ଡର ଅଡିଟ୍ ସାରାଂଶ।",
  guide_modal_sub: "ସାର୍ବଜନୀନ କ୍ରୟ ଅଧିକାରୀଙ୍କ ନିର୍ଦ୍ଦେଶିକା ଏବଂ ପ୍ରକ୍ରିୟା ସହାୟତା",
  lang_modal_sub: "ଭାରତର ଅଷ୍ଟମ ଅନୁସୂଚୀରେ ସ୍ୱୀକୃତିପ୍ରାପ୍ତ 20ଟି ସରକାରୀ ଆଞ୍ଚଳିକ ଭାଷା",
  footer_rights: "ସର୍ବସ୍ୱତ୍ୱ ସଂରକ୍ଷିତ। ଭାରତ ସରକାର।"
};

// 4. ASSAMESE (as)
const asFixes = {
  hero_kicker: "ভাৰতীয় মান • অধিক স্মাৰ্ট ক্ৰয়",
  hero_title: "কাৰিকৰী নিৰ্দিষ্টতাৰ পৰা সঠিক মানলৈ।",
  hero_desc: "এটা AI-চালিত প্লেটফৰ্ম যিয়ে চৰকাৰী বিভাগ আৰু PSUs ক উপযুক্ত ভাৰতীয় মান (BIS) চিনাক্ত কৰাত সহায় কৰে।",
  standards_subheading: "ব্যুৰো অৱ ইণ্ডিয়ান ষ্টেণ্ডাৰ্ডছ (BIS) ৰ চৰকাৰী ভঁৰাল যিয়ে সংস্কৰণ আৰু বাধ্যতামূলক DPIIT QCO অনুসৰণ কৰে।",
  standards_mandate_text: "BIS আইন ২০১৬ আৰু সাধাৰণ বিত্তীয় নিয়মাবলী (GFR ১৪৪) ৰ অধীনত চৰকাৰী ক্ৰয়ত ভাৰতীয় মান উল্লেখ কৰাটো বাধ্যতামূলক।",
  ws_desc: "অপ্ৰচলিত মান চিনাক্ত কৰিবলৈ আপোনাৰ নিবিদা নথি আপলোড কৰক।",
  dec_subtitle: "ডিজিটেল স্বাক্ষৰ আৰু প্ৰমাণৰ শৃংখলসহ CVC-অনুমোদিত সিদ্ধান্ত পেকেজ।",
  bidder_subtitle: "প্ৰস্তাবিত BIS মানৰ সৈতে নিবিদা দফাৰ তুলনা।",
  dash_subtitle: "সকলো মূল্যায়ন, QCO সন্মতি আৰু নিবিদা অডিটৰ সাৰাংশ।",
  guide_modal_sub: "ৰাজহুৱা ক্ৰয় বিষয়াৰ নিৰ্দেশিকা আৰু প্ৰক্ৰিয়া সহায়িকা",
  lang_modal_sub: "ভাৰতৰ ৮ম অনুসূচীত স্বীকৃত ২০টা চৰকাৰী আঞ্চলিক ভাষা",
  footer_rights: "সকলো অধিকাৰ সংৰক্ষিত। ভাৰত চৰকাৰ।"
};

// 5. SANTALI (sat)
const satFixes = {
  hero_kicker: "ᱵᱷᱟᱨᱚᱛᱤᱭᱚ ᱢᱟᱱᱚᱠ • ᱞᱟᱦᱟᱱᱛᱤ ᱠᱤᱨᱤᱧ",
  hero_title: "ᱴᱮᱠᱱᱤᱠᱟᱞ ᱠᱟᱛᱷᱟ ᱠᱷᱚᱱ ᱥᱟᱹᱨᱤ ᱢᱟᱱᱚᱠ ᱫᱷᱟᱹᱵᱤᱡ।",
  hero_desc: "ᱢᱤᱫᱴᱟᱝ AI ᱦᱚᱛᱮᱛᱮ ᱪᱟᱞᱟᱣᱜ ᱠᱟᱱ ᱵᱮᱵᱚᱥᱛᱷᱟ ᱡᱟᱦᱟᱸ ᱫᱚ ᱥᱚᱨᱠᱟᱨᱤ ᱚᱯᱷᱤᱥ ᱠᱚ ᱥᱟᱹᱨᱤ ᱢᱟᱱᱚᱠ (BIS) ᱯᱟᱸᱡᱟ ᱨᱮ ᱜᱚᱲᱚᱭ ᱮᱢᱟ ᱠᱟᱱᱟ᱾",
  standards_subheading: "BIS ᱨᱮᱱᱟᱜ ᱥᱚᱨᱠᱟᱨᱤ ᱢᱟᱱᱚᱠ ᱚᱲᱟᱜ ᱡᱟᱦᱟᱸ ᱫᱚ QCO ᱠᱚᱭ ᱧᱮᱞᱟ᱾",
  standards_mandate_text: "BIS ᱟᱹᱭᱤᱱ ᱒᱐᱑᱖ ᱟᱨ GFR ᱱᱤᱭᱚᱢ ᱑᱔᱔ ᱞᱮᱠᱟᱛᱮ ᱥᱚᱨᱠᱟᱨᱤ ᱠᱤᱨᱤᱧ ᱨᱮ ᱵᱷᱟᱨᱚᱛᱤᱭᱚ ᱢᱟᱱᱚᱠ ᱵᱮᱵᱷᱟᱨ ᱫᱚ ᱵᱟᱫᱷᱭᱚᱛᱟᱢᱩᱞᱚᱠ ᱠᱟᱱᱟ᱾",
  ws_desc: "ᱢᱟᱨᱮ ᱢᱟᱱᱚᱠ ᱧᱟᱢ ᱞᱟᱹᱜᱤᱫ ᱴᱮᱱᱰᱟᱨ ᱚᱞ ᱟᱯᱞᱳᱰ ᱢᱮ᱾",
  dec_subtitle: "ᱰᱤᱡᱤᱴᱟᱞ ᱥᱤᱞ ᱥᱟᱶ CVC ᱢᱟᱱᱟᱣ ᱜᱚᱴᱟ ᱯᱮᱠᱮᱡ᱾",
  bidder_subtitle: "BIS ᱢᱟᱱᱚᱠ ᱥᱟᱶ ᱴᱮᱱᱰᱟᱨ ᱨᱮᱱᱟᱜ ᱥᱚᱢᱟᱱ ᱵᱤᱰᱟᱹᱣ᱾",
  dash_subtitle: "ᱡᱚᱛᱚ ᱵᱤᱰᱟᱹᱣ ᱟᱨ ᱴᱮᱱᱰᱟᱨ ᱚᱰᱤᱴ ᱨᱮᱱᱟᱜ ᱥᱟᱨᱟᱝᱥᱚ᱾",
  guide_modal_sub: "ᱥᱚᱨᱠᱟᱨᱤ ᱠᱤᱨᱤᱧ ᱚᱯᱷᱤᱥᱚᱨ ᱠᱚᱣᱟᱜ ᱫᱤᱥᱟᱹ ᱩᱫᱩᱜ",
  lang_modal_sub: "ᱵᱷᱟᱨᱚᱛ ᱨᱮᱱᱟᱜ ᱘ ᱟᱱ ᱚᱱᱩᱥᱩᱪᱤ ᱨᱮ ᱒᱐ ᱜᱚᱴᱟᱝ ᱨᱟᱡᱽᱵᱷᱟᱥᱟ",
  footer_rights: "ᱡᱚᱛᱚ ᱦᱚᱠ ᱨᱩᱠᱷᱤᱭᱟᱹ ᱢᱮᱱᱟᱜᱼᱟ᱾ ᱵᱷᱟᱨᱚᱛ ᱥᱚᱨᱠᱟᱨ᱾"
};

// 6. KASHMIRI (ks)
const ksFixes = {
  ws_desc: "پرٲنؠ معیار ژھارنہٕ خٲطرٕ پَنُن ٹینڈر دستاویز اَپ لوڈ کٔرِو۔",
  dec_subtitle: "ڈیجیٹل دستخط تہٕ ثبوتن ہٕنٛز لڑی سٟتؠ CVC مطٲبق فیصلہٕ پیکیج۔",
  bidder_subtitle: "تجویز کَرنہٕ آمٕتین BIS معیاراتن سٟتؠ ٹینڈر شقن ہُنٛد تقابل۔",
  dash_subtitle: "تمام جائزہ، QCO تعمیل تہٕ ٹینڈر آڈٹُک خلاصہٕ۔",
  guide_modal_sub: "سرکٲرؠ پروکیورمنٹ افسر گائیڈ تہٕ طریقہٕ کار مدد",
  lang_modal_sub: "ہندوستان کس 8 مہِ شیڈولس منٛز تسلیم شدہ 20 سرکٲرؠ علاقٲیی زبانن"
};

const remainingFixes = {
  bn: bnFixes,
  pa: paFixes,
  or: orFixes,
  as: asFixes,
  sat: satFixes,
  ks: ksFixes
};

for (const [lang, fixes] of Object.entries(remainingFixes)) {
  if (resourcesObj[lang]) {
    resourcesObj[lang].translation = {
      ...resourcesObj[lang].translation,
      ...fixes
    };
  }
}

// Write back
const output = `export const resources: Record<string, { translation: Record<string, string> }> = ${JSON.stringify(resourcesObj, null, 2)};\n`;
fs.writeFileSync(resourcesFile, output, 'utf8');
console.log('Successfully applied remaining native translations for bn, pa, or, as, sat, ks!');

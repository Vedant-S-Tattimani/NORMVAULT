export interface LanguageOption {
  code: string;
  name: string;
  nativeName: string;
  script: string;
  region: string;
}

export const SUPPORTED_LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English', script: 'Latin', region: 'Pan-India & Global' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari', region: 'North / Central' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', script: 'Bengali', region: 'West Bengal / Tripura' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu', region: 'Andhra Pradesh / Telangana' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', script: 'Devanagari', region: 'Maharashtra' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil', region: 'Tamil Nadu / Puducherry' },
  { code: 'ur', name: 'Urdu', nativeName: 'اردو', script: 'Arabic-Persian', region: 'Pan-India' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', script: 'Gujarati', region: 'Gujarat' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada', region: 'Karnataka' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', script: 'Odia', region: 'Odisha' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam', region: 'Kerala / Lakshadweep' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', script: 'Gurmukhi', region: 'Punjab / North' },
  { code: 'as', name: 'Assamese', nativeName: 'অসমীয়া', script: 'Bengali-Assamese', region: 'Assam / North-East' },
  { code: 'mai', name: 'Maithili', nativeName: 'मैथिली', script: 'Devanagari', region: 'Bihar / Jharkhand' },
  { code: 'sat', name: 'Santali', nativeName: 'ᱥᱟᱱᱛᱟᱲᱤ', script: 'Ol Chiki', region: 'Jharkhand / Odisha / WB' },
  { code: 'ks', name: 'Kashmiri', nativeName: 'कॉशुर', script: 'Devanagari / Nastaliq', region: 'Jammu & Kashmir' },
  { code: 'ne', name: 'Nepali', nativeName: 'नेपाली', script: 'Devanagari', region: 'Sikkim / West Bengal' },
  { code: 'kok', name: 'Konkani', nativeName: 'कोंकणी', script: 'Devanagari', region: 'Goa / Maharashtra / Karnataka' },
  { code: 'sd', name: 'Sindhi', nativeName: 'सिन्धी', script: 'Devanagari / Arabic', region: 'Pan-India' },
  { code: 'doi', name: 'Dogri', nativeName: 'डोगरी', script: 'Devanagari', region: 'Jammu & Kashmir' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', script: 'Devanagari', region: 'Classical National' },
];

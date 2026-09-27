import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { resources } from './resources';

const savedLanguage = typeof window !== 'undefined'
  ? localStorage.getItem('normvault_language') || 'en'
  : 'en';

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: savedLanguage,
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false, // React already escapes values
    },
  });

export function changeAppLanguage(langCode: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('normvault_language', langCode);
  }
  i18n.changeLanguage(langCode);
}

export default i18n;

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import translationEN from './locales/en/translation.json';
import translationFR from './locales/fr/translation.json';

// Define the available translations
const resources = {
    en: {
        translation: translationEN
    },
    fr: {
        translation: translationFR
    }
};

i18n
    // Detect user language automatically
    .use(LanguageDetector)
    // Hook up to react-i18next
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'fr', // Fallback to French
        debug: true,

        interpolation: {
            escapeValue: false // React already escapes values to prevent XSS
        }
    });

export default i18n;

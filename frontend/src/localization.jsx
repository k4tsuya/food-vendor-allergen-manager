import { createContext, useContext, useState, useEffect } from 'react';

const translations = {
  nl: {
    pageTitle: 'Product Allergieën',
    loading: 'Producten laden...',
    noAllergens: 'Geen bekende allergenen',
    disclaimer: 'Deze informatie is bedoeld als hulpmiddel. Controleer altijd bij het personeel voordat u iets bestelt met een allergie of intolerantie.',
  },
  en: {
    pageTitle: 'Product Allergies',
    loading: 'Loading products...',
    noAllergens: 'No known allergens',
    disclaimer: 'This information is a guide only. Always confirm with staff before ordering if you have an allergy or intolerance.',
  },
};

const LanguageContext = createContext(null);

export function LanguageProvider({ children }) {
  const [language, setLanguage] = useState('nl');
  const [hasLoadedDefault, setHasLoadedDefault] = useState(false);

  useEffect(() => {
    fetch('http://localhost:8000/config')
      .then((res) => res.json())
      .then((data) => {
        setLanguage(data.default_language);
        setHasLoadedDefault(true);
      });
  }, []);

  const t = translations[language];

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t, hasLoadedDefault }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  return useContext(LanguageContext);
}
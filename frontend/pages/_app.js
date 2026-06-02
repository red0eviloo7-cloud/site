import React, { useEffect } from 'react';
import '../styles/globals.css';
import i18n from '../config/i18n';
import { useRouter } from 'next/router';

function MyApp({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    // Initialize i18n
    i18n.init().catch(err => console.error('i18n initialization error:', err));
    
    // Set language from query or localStorage
    const lang = router.query.lang || localStorage.getItem('language') || 'en';
    i18n.changeLanguage(lang);
  }, [router.query.lang]);

  return <Component {...pageProps} />;
}

export default MyApp;

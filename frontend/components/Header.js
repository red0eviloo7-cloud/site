import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useRouter } from 'next/router';
import styles from '../styles/Header.module.css';

const Header = () => {
  const { t, i18n } = useTranslation();
  const router = useRouter();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Español' },
    { code: 'fr', name: 'Français' },
    { code: 'de', name: 'Deutsch' },
    { code: 'ja', name: '日本語' }
  ];

  const handleLanguageChange = (lang) => {
    i18n.changeLanguage(lang);
    localStorage.setItem('language', lang);
    router.push(router.pathname, router.asPath, { locale: lang });
  };

  return (
    <header className={styles.header}>
      <nav className={styles.navbar}>
        <div className={styles.container}>
          <div className={styles.logo}>
            <span className={styles.logoText}>SYTISEC</span>
            <span className={styles.tagline}>{t('tagline')}</span>
          </div>
          
          <div className={styles.menu}>
            <ul className={styles.navLinks}>
              <li><a href="#services">{t('services')}</a></li>
              <li><a href="#about">{t('about')}</a></li>
              <li><a href="#directors">{t('team')}</a></li>
              <li><a href="#contact">{t('contact')}</a></li>
            </ul>
            
            <div className={styles.languageSelector}>
              <select 
                onChange={(e) => handleLanguageChange(e.target.value)}
                value={i18n.language}
                className={styles.languageSelect}
              >
                {languages.map(lang => (
                  <option key={lang.code} value={lang.code}>
                    {lang.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <button 
            className={styles.mobileMenuBtn}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            ☰
          </button>
        </div>
      </nav>
    </header>
  );
};

export default Header;

import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../styles/Hero.module.css';

const Hero = () => {
  const { t } = useTranslation();
  const [animatedText, setAnimatedText] = useState('');
  const fullText = t('hero_title');
  const typingSpeed = 50;

  useEffect(() => {
    let index = 0;
    const interval = setInterval(() => {
      if (index <= fullText.length) {
        setAnimatedText(fullText.substring(0, index));
        index++;
      } else {
        clearInterval(interval);
      }
    }, typingSpeed);
    
    return () => clearInterval(interval);
  }, [fullText, typingSpeed]);

  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <div className={styles.heroText}>
          <h1 className={styles.heroTitle}>{animatedText}<span className={styles.cursor}>|</span></h1>
          <p className={styles.heroSubtitle}>{t('hero_subtitle')}</p>
          <button className={styles.ctaButton}>{t('get_started')}</button>
        </div>
        <div className={styles.heroImage}>
          <div className={styles.imagePlaceholder}>
            <div className={styles.logoContainer}>SYTISEC</div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;

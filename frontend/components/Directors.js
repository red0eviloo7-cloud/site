import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../styles/Directors.module.css';

const Directors = ({ directors }) => {
  const { t } = useTranslation();

  return (
    <section id="directors" className={styles.directors}>
      <div className={styles.container}>
        <h2 className={styles.title}>{t('leadership_team')}</h2>
        <p className={styles.subtitle}>{t('team_description')}</p>
        
        <div className={styles.directorsGrid}>
          {directors && directors.map((director, index) => (
            <div key={index} className={styles.directorCard}>
              <div className={styles.directorImage}>
                <div className={styles.imagePlaceholder}>{director.name.charAt(0)}</div>
              </div>
              <h3 className={styles.directorName}>{director.name}</h3>
              <p className={styles.directorTitle}>{director.title}</p>
              <p className={styles.directorBio}>{director.bio}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Directors;

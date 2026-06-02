import React from 'react';
import { useTranslation } from 'react-i18next';
import styles from '../styles/Services.module.css';

const Services = ({ services }) => {
  const { t } = useTranslation();

  return (
    <section id="services" className={styles.services}>
      <div className={styles.container}>
        <h2 className={styles.title}>{t('our_services')}</h2>
        <p className={styles.subtitle}>{t('services_description')}</p>
        
        <div className={styles.servicesGrid}>
          {services && services.map((service) => (
            <div key={service.id} className={styles.serviceCard}>
              <div className={styles.serviceIcon}>{service.icon}</div>
              <h3 className={styles.serviceName}>{service.name}</h3>
              <p className={styles.serviceDescription}>{service.description}</p>
              <button className={styles.learnMore}>{t('learn_more')}</button>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Services;

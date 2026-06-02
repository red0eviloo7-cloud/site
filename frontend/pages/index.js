import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import Header from '../components/Header';
import Hero from '../components/Hero';
import Services from '../components/Services';
import Directors from '../components/Directors';
import ContactForm from '../components/ContactForm';
import Footer from '../components/Footer';
import styles from '../styles/Home.module.css';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

export default function Home() {
  const { t } = useTranslation();
  const [services, setServices] = useState([]);
  const [directors, setDirectors] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [servicesRes, directorsRes] = await Promise.all([
          axios.get(`${API_URL}/services`),
          axios.get(`${API_URL}/directors`)
        ]);
        
        if (servicesRes.data?.services) setServices(servicesRes.data.services);
        if (directorsRes.data?.directors) setDirectors(directorsRes.data.directors);
      } catch (error) {
        console.error('Error fetching data:', error);
      }
    };
    
    fetchData();
  }, []);

  return (
    <div className={styles.container}>
      <Header />
      <Hero />
      <Services services={services} />
      <Directors directors={directors} />
      <ContactForm />
      <Footer />
    </div>
  );
}

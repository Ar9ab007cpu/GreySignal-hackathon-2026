import { useEffect, useState } from 'react';
import { getCountries, submitAssessment } from './api';
import Header from './components/Header';
import Footer from './components/Footer';
import Wizard from './components/Wizard';
import Overview from './components/Overview';
import Results from './components/Results';

const DEFAULT_FORM = {
  country: 'Vietnam',
  sector: 'Manufacturing expansion',
  city_or_port: 'Hai Phong',
  investment_size: 'Medium',
  entry_mode: 'Greenfield',
  time_horizon: '12-24 months',
  risk_tolerance: 'Medium',
  labor_intensity: 'Medium',
  supply_chain_dependence: 'Medium',
  regulatory_sensitivity: 'Medium',
  local_partner_available: false,
  news_keywords: 'strike OR protest OR election OR tariff OR supply chain',
  base_currency: 'USD',
  target_currency: 'VND',
  hs_code: 'TOTAL',
  start_year: 2020,
  end_year: 2026,
};

export default function App() {
  const [countries, setCountries] = useState([]);
  const [formData, setFormData] = useState(DEFAULT_FORM);
  const [wizardStep, setWizardStep] = useState(0);
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getCountries().then(setCountries);
  }, []);

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await submitAssessment(formData);
      setAssessment(result);
    } catch (err) {
      setError(err.message || 'Assessment failed. Check that the FastAPI backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-wrapper">
      <Header />

      <main className="app-main">
        {/* Wizard (always visible) */}
        <Wizard
          step={wizardStep}
          formData={formData}
          countries={countries}
          onFormChange={setFormData}
          onStepChange={(s) => setWizardStep(Math.max(0, Math.min(s, 4)))}
          onSubmit={handleSubmit}
        />

        <hr className="divider" />

        {/* Error */}
        {error && (
          <div className="error-banner">
            {error}
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div className="loading-overlay">
            <div className="loading-spinner" />
            <div className="loading-text">Collecting public signals and scoring risk...</div>
          </div>
        )}

        {/* Results or Overview */}
        {!loading && assessment && <Results assessment={assessment} />}
        {!loading && !assessment && !error && <Overview />}
      </main>

      <Footer />
    </div>
  );
}

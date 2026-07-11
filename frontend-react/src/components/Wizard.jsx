const STEPS = ['Market', 'Investment', 'Exposure', 'Data', 'Review'];

function StepIndicator({ current }) {
  return (
    <div className="step-indicator">
      {STEPS.map((name, i) => {
        const cls = i < current ? 'done' : i === current ? 'active' : 'pending';
        return (
          <div key={name} style={{ display: 'flex', alignItems: 'center' }}>
            <div className="step-node">
              <div className={`step-circle ${cls}`}>{i + 1}</div>
              <div className={`step-label ${cls}`}>{name}</div>
            </div>
            {i < STEPS.length - 1 && (
              <div className={`step-line ${i < current ? 'done' : 'pending'}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}

export default function Wizard({
  step,
  formData,
  countries,
  onFormChange,
  onStepChange,
  onSubmit,
}) {
  const update = (field) => (e) => {
    const value = e.target.type === 'checkbox' ? e.target.checked : e.target.value;
    onFormChange({ ...formData, [field]: value });
  };

  const reviewRows = [
    ['Country', formData.country],
    ['Sector', formData.sector],
    ['City / port', formData.city_or_port],
    ['Investment size', formData.investment_size],
    ['Entry mode', formData.entry_mode],
    ['Time horizon', formData.time_horizon],
    ['Risk tolerance', formData.risk_tolerance],
    ['Labor intensity', formData.labor_intensity],
    ['Supply-chain', formData.supply_chain_dependence],
    ['Regulatory', formData.regulatory_sensitivity],
    ['Currencies', `${formData.base_currency} → ${formData.target_currency}`],
  ];

  return (
    <div className="wizard-wrapper">
      <h2 className="assessment-title">Assessment</h2>
      <StepIndicator current={step} />

      {/* Step 0 - Market */}
      {step === 0 && (
        <>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-country">Target country</label>
            <select
              id="wiz-country"
              className="form-select"
              value={formData.country}
              onChange={update('country')}
            >
              {countries.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-sector">Sector or decision</label>
            <input
              id="wiz-sector"
              className="form-input"
              value={formData.sector}
              onChange={update('sector')}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-city">City or port</label>
            <input
              id="wiz-city"
              className="form-input"
              value={formData.city_or_port}
              onChange={update('city_or_port')}
            />
          </div>
        </>
      )}

      {/* Step 1 - Investment */}
      {step === 1 && (
        <>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-size">Investment size</label>
            <select id="wiz-size" className="form-select" value={formData.investment_size} onChange={update('investment_size')}>
              {['Small', 'Medium', 'Large'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-mode">Entry mode</label>
            <select id="wiz-mode" className="form-select" value={formData.entry_mode} onChange={update('entry_mode')}>
              {['Exporting', 'Joint venture', 'Greenfield', 'Acquisition'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-horizon">Time horizon</label>
            <select id="wiz-horizon" className="form-select" value={formData.time_horizon} onChange={update('time_horizon')}>
              {['0-6 months', '6-12 months', '12-24 months', '24+ months'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-risk">Risk tolerance</label>
            <select id="wiz-risk" className="form-select" value={formData.risk_tolerance} onChange={update('risk_tolerance')}>
              {['Low', 'Medium', 'High'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
        </>
      )}

      {/* Step 2 - Exposure */}
      {step === 2 && (
        <>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-labor">Labor intensity</label>
            <select id="wiz-labor" className="form-select" value={formData.labor_intensity} onChange={update('labor_intensity')}>
              {['Low', 'Medium', 'High'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-sc">Supply-chain dependence</label>
            <select id="wiz-sc" className="form-select" value={formData.supply_chain_dependence} onChange={update('supply_chain_dependence')}>
              {['Low', 'Medium', 'High'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-reg">Regulatory sensitivity</label>
            <select id="wiz-reg" className="form-select" value={formData.regulatory_sensitivity} onChange={update('regulatory_sensitivity')}>
              {['Low', 'Medium', 'High'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-checkbox-row">
              <input
                type="checkbox"
                className="form-checkbox"
                checked={formData.local_partner_available}
                onChange={update('local_partner_available')}
              />
              <span className="form-checkbox-label">Local partner available</span>
            </label>
          </div>
        </>
      )}

      {/* Step 3 - Data */}
      {step === 3 && (
        <>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-base-cur">Base currency</label>
            <select id="wiz-base-cur" className="form-select" value={formData.base_currency} onChange={update('base_currency')}>
              {['USD', 'EUR', 'GBP', 'INR'].map((o) => <option key={o}>{o}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-target-cur">Target currency</label>
            <input
              id="wiz-target-cur"
              className="form-input"
              value={formData.target_currency}
              onChange={(e) => onFormChange({ ...formData, target_currency: e.target.value.toUpperCase().slice(0, 3) })}
              maxLength={3}
            />
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-hs">HS code</label>
            <input id="wiz-hs" className="form-input" value={formData.hs_code} onChange={update('hs_code')} />
          </div>
          <div className="form-group">
            <label className="form-label">World Bank year range</label>
            <div className="year-range-row">
              <div>
                <input
                  type="number"
                  className="form-input"
                  value={formData.start_year}
                  min={2015}
                  max={formData.end_year}
                  onChange={(e) => onFormChange({ ...formData, start_year: Number(e.target.value) })}
                  placeholder="Start year"
                />
              </div>
              <div>
                <input
                  type="number"
                  className="form-input"
                  value={formData.end_year}
                  min={formData.start_year}
                  max={2026}
                  onChange={(e) => onFormChange({ ...formData, end_year: Number(e.target.value) })}
                  placeholder="End year"
                />
              </div>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label" htmlFor="wiz-kw">News keywords</label>
            <textarea
              id="wiz-kw"
              className="form-textarea"
              value={formData.news_keywords}
              onChange={update('news_keywords')}
            />
          </div>
        </>
      )}

      {/* Step 4 - Review */}
      {step === 4 && (
        <>
          <div className="table-wrapper mb-4">
            <table className="review-table">
              <tbody>
                {reviewRows.map(([label, value]) => (
                  <tr key={label}>
                    <td>{label}</td>
                    <td>{String(value)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <button className="btn btn-primary btn-full" onClick={onSubmit}>
            Start assessment
          </button>
        </>
      )}

      {/* Navigation */}
      <div className="btn-row mt-4">
        <button
          className="btn btn-secondary"
          disabled={step === 0}
          onClick={() => onStepChange(step - 1)}
        >
          Back
        </button>
        <button
          className="btn btn-secondary"
          disabled={step === STEPS.length - 1}
          onClick={() => onStepChange(step + 1)}
        >
          Next
        </button>
      </div>
    </div>
  );
}

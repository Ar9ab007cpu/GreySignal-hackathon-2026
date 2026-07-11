/* ================================================================
   HOME HERO  --  What GreySignal is and what it does
   ================================================================ */

const STEPS = [
  {
    num: '01',
    title: 'Describe your move',
    text: 'Choose a target country, sector, entry mode, and your operating exposure — investment size, supply-chain and labour intensity, time horizon, and risk tolerance.',
  },
  {
    num: '02',
    title: 'We gather the evidence',
    text: 'GreySignal pulls live public signals: World Bank economics, WGI governance, currency rates, weather exposure, trade flows, and real-time news — in parallel, in seconds.',
  },
  {
    num: '03',
    title: 'Get a scored decision',
    text: 'A weighted model plus an XGBoost / CatBoost / LightGBM ensemble returns a 0–100 risk score, a clear proceed / delay / rethink recommendation, and the evidence behind it.',
  },
];

const SIGNALS = [
  'Macroeconomic growth',
  'Inflation',
  'Political stability',
  'Currency',
  'Weather',
  'Trade flows',
  'News & events',
];

export default function Hero() {
  return (
    <section className="hero">
      <div className="hero-badge">Geopolitical Business Risk Intelligence</div>

      <h1 className="hero-title">
        Know the risk <span>before</span> you expand.
      </h1>

      <p className="hero-lead">
        Entering or scaling in a new market is a high-stakes bet. GreySignal turns scattered
        public economic, political, trade, weather, currency, and news signals into a single,
        evidence-backed risk score — so you can decide whether to <strong>proceed</strong>,{' '}
        <strong>delay</strong>, or <strong>rethink</strong> in minutes, not weeks.
      </p>

      <div className="hero-signals">
        {SIGNALS.map((signal) => (
          <span className="hero-signal-chip" key={signal}>{signal}</span>
        ))}
      </div>

      <div className="hero-steps">
        {STEPS.map((step) => (
          <div className="hero-step" key={step.num}>
            <div className="hero-step-num">{step.num}</div>
            <h4 className="hero-step-title">{step.title}</h4>
            <p className="hero-step-text">{step.text}</p>
          </div>
        ))}
      </div>

      <div className="hero-cta-hint">
        <span className="hero-cta-dot" />
        Start with the guided assessment below
      </div>
    </section>
  );
}

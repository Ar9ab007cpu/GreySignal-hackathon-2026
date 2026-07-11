export default function Overview() {
  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '20px 0' }}>
      <h2>GreySignal Overview</h2>
      <p className="mt-4">
        GreySignal is a decision-support workspace for evaluating geopolitical and business risk before
        entering or expanding in a market. It combines real macroeconomic data, governance indicators,
        currency signals, weather exposure, trade context, and news/event monitoring into a single assessment.
      </p>

      <div className="overview-grid">
        <div className="overview-panel">
          <h4>What It Answers</h4>
          <p>
            Whether a company should proceed, delay, or redesign an expansion plan based on country risk,
            operating exposure, and business fit.
          </p>
        </div>
        <div className="overview-panel">
          <h4>Evidence Used</h4>
          <p>
            World Bank WDI/WGI, exchange rates, Open-Meteo weather signals, GDELT news, UN Comtrade trade
            data, and user-provided operating context.
          </p>
        </div>
        <div className="overview-panel">
          <h4>Analysis Produced</h4>
          <p>
            Risk score, recommendation, AI executive brief, agent findings, forecasts, SHAP explanation,
            MAPIE confidence interval, and knowledge graph.
          </p>
        </div>
        <div className="overview-panel">
          <h4>Workflow</h4>
          <p>
            LangGraph coordinates assessment initialization, evidence collection, validation, scoring,
            model explanation, and final response generation.
          </p>
        </div>
        <div className="overview-panel">
          <h4>Machine Learning</h4>
          <p>
            XGBoost, CatBoost, and LightGBM train from a real country-year dataset built from World Bank
            WDI and WGI indicators.
          </p>
        </div>
        <div className="overview-panel">
          <h4>How To Use</h4>
          <p>
            Complete the guided questions above. On the review step, select Start assessment. This
            documentation will be replaced by the results.
          </p>
        </div>
      </div>

      <div className="overview-note">
        GreySignal is designed for early-stage decision intelligence. It does not replace legal, compliance,
        security, or in-country expert due diligence.
      </div>
    </div>
  );
}

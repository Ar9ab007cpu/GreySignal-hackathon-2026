export default function Footer({ onNavigate }) {
  const year = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-inner">
        <div className="footer-col">
          <strong>GreySignal</strong>
          Business expansion risk intelligence for country, sector, and supply-chain decisions.
        </div>
        <div className="footer-col">
          <strong>Evidence-led assessment</strong>
          Combines economic, political, trade, weather, currency, and news signals into a structured risk view.
        </div>
        <div className="footer-col">
          <strong>Decision support</strong>
          Designed to support early due diligence; final decisions should include expert, legal, and local review.
        </div>
      </div>

      <div className="footer-bottom">
        <span className="footer-copyright">
          © {year} GreySignal. All rights reserved.
        </span>
        <div className="footer-bottom-links">
          <button className="footer-link-btn" onClick={() => onNavigate && onNavigate('developers')}>
            Developers
          </button>
          <a href="https://github.com/Ar9ab007cpu/GreySignal-hackathon-2026" target="_blank" rel="noreferrer">
            GitHub
          </a>
        </div>
      </div>
    </footer>
  );
}

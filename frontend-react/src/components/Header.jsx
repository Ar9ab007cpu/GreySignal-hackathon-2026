export default function Header({ view = 'app', onNavigate }) {
  const go = (target) => () => onNavigate && onNavigate(target);

  return (
    <header className="header">
      <div className="header-inner">
        <div
          className="header-brand"
          onClick={go('app')}
          style={{ cursor: onNavigate ? 'pointer' : 'default' }}
        >
          <div className="header-logo" />
          <div>
            <div className="header-title">GreySignal</div>
            <div className="header-subtitle">Geopolitical business risk intelligence</div>
          </div>
        </div>

        {onNavigate && (
          <nav className="header-nav">
            <button
              className={`header-nav-link ${view === 'app' ? 'active' : ''}`}
              onClick={go('app')}
            >
              Assessment
            </button>
            <button
              className={`header-nav-link ${view === 'developers' ? 'active' : ''}`}
              onClick={go('developers')}
            >
              Developers
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}

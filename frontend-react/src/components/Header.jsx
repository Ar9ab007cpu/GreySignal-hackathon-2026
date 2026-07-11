export default function Header({ onNavigate }) {
  const goHome = () => onNavigate && onNavigate('app');

  return (
    <header className="header">
      <div className="header-inner">
        <div
          className="header-brand"
          onClick={goHome}
          style={{ cursor: onNavigate ? 'pointer' : 'default' }}
        >
          <div className="header-logo" />
          <div>
            <div className="header-title">GreySignal</div>
            <div className="header-subtitle">Geopolitical business risk intelligence</div>
          </div>
        </div>

        <div className="header-tag">Decision Intelligence</div>
      </div>
    </header>
  );
}

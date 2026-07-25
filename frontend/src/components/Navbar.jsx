import { useLanguage } from '../localization.jsx';

function Navbar() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <nav className="navbar">
      <span className="navbar-brand">{t.brand}</span>
      <div className="navbar-links">
        
        <a  href={`http://localhost:8000/items/pdf?language=${language}`}
          className="navbar-link navbar-link-icon"
        >
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          Download PDF
        </a>
        <button
          onClick={() => setLanguage(language === 'nl' ? 'en' : 'nl')}
          className="language-switcher"
        >
          {language === 'nl' ? 'NL' : 'EN'}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
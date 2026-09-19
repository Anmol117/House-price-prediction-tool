import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, Info, Building2 } from 'lucide-react';

export const Navbar: React.FC = () => {
  const location = useLocation();

  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <div className="navbar-logo">
            <Building2 size={24} />
          </div>
          <div className="navbar-title-group">
            <span className="navbar-title">HomeValuate</span>
            <span className="navbar-subtitle">AI Price Predictor</span>
          </div>
        </Link>

        <nav className="navbar-nav">
          <Link
            to="/"
            className={`nav-link ${location.pathname === '/' ? 'active' : ''}`}
          >
            <Home size={18} />
            <span>Predictor</span>
          </Link>
          <Link
            to="/about"
            className={`nav-link ${location.pathname === '/about' ? 'active' : ''}`}
          >
            <Info size={18} />
            <span>About Model</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};

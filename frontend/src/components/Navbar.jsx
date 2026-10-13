import React from 'react';

export default function Navbar({ activeTab, setActiveTab, health, onRerunMatch, isMatching }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '📊' },
    { id: 'upload', label: 'Upload Data', icon: '📁' },
    { id: 'matches', label: 'Entity Matches', icon: '🔗' },
    { id: 'entities', label: 'Entities', icon: '🏢' },
    { id: 'compare', label: 'Live Matcher', icon: '🔬' },
    { id: 'statistics', label: 'Statistics', icon: '📈' },
    { id: 'evaluation', label: 'Evaluation', icon: '🎯' },
  ];

  return (
    <nav className="navbar">
      <div className="nav-inner">
        <div className="brand">
          <div className="brand-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm6 12H6v-1.4c0-2 4-3.1 6-3.1s6 1.1 6 3.1V18z"/>
            </svg>
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <span className="brand-title">EntityResolve</span>
              <span className="brand-badge">ML AI</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#64748b' }}>Enterprise Business Entity Resolution</div>
          </div>
        </div>

        <ul className="nav-links">
          {navItems.map((item) => (
            <li key={item.id}>
              <button
                className={`nav-btn ${activeTab === item.id ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </button>
            </li>
          ))}
        </ul>

        <div className="nav-status">
          <button
            className="btn btn-secondary btn-sm"
            onClick={onRerunMatch}
            disabled={isMatching}
            title="Re-run matching pipeline"
          >
            {isMatching ? '⚡ Matching...' : '⚡ Re-Run Resolution'}
          </button>
          
          <div className="status-pill" title={health?.model_loaded ? 'RandomForest ML Active' : 'Heuristic Mode'}>
            <span className="status-dot"></span>
            <span>{health?.status === 'healthy' ? (health.model_loaded ? 'ML Online' : 'Active') : 'Connecting'}</span>
          </div>
        </div>
      </div>
    </nav>
  );
}

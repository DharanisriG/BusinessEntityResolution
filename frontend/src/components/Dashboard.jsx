import React from 'react';

export default function Dashboard({ stats, onNavigate, onRerunMatch, isMatching }) {
  if (!stats) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <div style={{ fontSize: '1.2rem', color: '#94a3b8' }}>Loading dashboard statistics...</div>
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Records',
      value: stats.total_records || 0,
      desc: 'Ingested across all sources',
      accent: '#6366F1',
      icon: '📑'
    },
    {
      label: 'Unique Entities',
      value: stats.unique_entities || 0,
      desc: 'Distinct canonical businesses',
      accent: '#06B6D4',
      icon: '🏢'
    },
    {
      label: 'Potential Matches',
      value: stats.potential_matches || 0,
      desc: 'Candidate cross-source pairs',
      accent: '#F59E0B',
      icon: '🔗'
    },
    {
      label: 'High Confidence',
      value: stats.high_confidence_matches || 0,
      desc: 'Matches with score ≥ 75%',
      accent: '#10B981',
      icon: '✨'
    },
    {
      label: 'Duplicate Records',
      value: stats.duplicate_records || 0,
      desc: 'Redundant rows consolidated',
      accent: '#8B5CF6',
      icon: '🧹'
    }
  ];

  return (
    <div>
      {/* Top Banner Header */}
      <div className="page-header">
        <div>
          <h1 className="page-title">Business Entity Resolution</h1>
          <p className="page-subtitle">
            Identify and consolidate duplicate business records across multiple data sources.
            Combines robust normalization, multi-key blocking, RapidFuzz similarity scoring, and machine-learning classification.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => onNavigate('upload')}>
            📁 Upload Sources
          </button>
          <button className="btn btn-primary" onClick={() => onNavigate('matches')}>
            🔗 View Matched Pairs
          </button>
        </div>
      </div>

      {/* 5 Required Metrics Cards */}
      <div className="stats-grid">
        {statCards.map((card, idx) => (
          <div key={idx} className="stat-card" style={{ '--card-accent': card.accent }}>
            <div className="stat-header">
              <span className="stat-label">{card.label}</span>
              <span className="stat-icon" style={{ fontSize: '1.1rem' }}>{card.icon}</span>
            </div>
            <div className="stat-value">{card.value.toLocaleString()}</div>
            <div className="stat-desc">{card.desc}</div>
          </div>
        ))}
      </div>

      {/* Overview Analytics Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Confidence Tier Breakdown Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Confidence Distribution</h2>
              <div className="card-desc">Pairwise classification tiers across candidate pairs</div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('statistics')}>
              Detailed Analytics →
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {Object.entries(stats.confidence_distribution || {}).map(([tier, count]) => {
              const total = stats.potential_matches || 1;
              const pct = Math.round((count / Math.max(1, Object.values(stats.confidence_distribution).reduce((a, b) => a + b, 0))) * 100);
              
              let barColor = '#6366F1';
              if (tier.includes('Very High')) barColor = '#10B981';
              else if (tier.includes('High')) barColor = '#06B6D4';
              else if (tier.includes('Possible')) barColor = '#F59E0B';
              else if (tier.includes('Low')) barColor = '#F97316';
              else barColor = '#64748B';

              return (
                <div key={tier}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{tier}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>
                      {count} pairs ({pct}%)
                    </span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${Math.min(100, pct * 1.5 || (count > 0 ? 5 : 0))}%`, backgroundColor: barColor }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Source Breakdown Card */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Sources Distribution</h2>
              <div className="card-desc">Records ingested per data source</div>
            </div>
            <button className="btn btn-secondary btn-sm" onClick={() => onNavigate('upload')}>
              Manage Sources →
            </button>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {Object.entries(stats.records_per_source || {}).map(([src, count]) => {
              const pct = Math.round((count / Math.max(1, stats.total_records)) * 100);
              return (
                <div key={src} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '0.9rem 1.1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <span style={{ fontWeight: 700, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="badge badge-source">{src}</span>
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: '#38bdf8' }}>
                      {count} records ({pct}%)
                    </span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${pct}%`, backgroundColor: '#06B6D4' }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div style={{ marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', color: '#94a3b8' }}>
            <span>Resolved Deduplication Rate:</span>
            <span style={{ fontWeight: 700, color: '#34D399', fontFamily: 'var(--font-mono)' }}>
              {stats.total_records ? Math.round((stats.duplicate_records / stats.total_records) * 100) : 0}% Reduction
            </span>
          </div>
        </div>
      </div>

      {/* Quick Explanatory Banner for Viva / Demonstration */}
      <div className="card" style={{ background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(6, 182, 212, 0.05))', border: '1px solid rgba(99, 102, 241, 0.25)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ fontSize: '2rem' }}>💡</div>
          <div style={{ flex: 1 }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.2rem' }}>
              How Business Entity Resolution Works
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.4' }}>
              Records from heterogeneous systems (varying legal suffixes like <em>Pvt Ltd</em> vs <em>Private Limited</em>, messy phone formats, typos, and abbreviations) are normalized, blocked via multi-index hashing, compared across 15 pairwise similarity features, and classified with a trained Random Forest model into unified <strong>Canonical Business Profiles</strong>.
            </p>
          </div>
          <button className="btn btn-primary btn-sm" onClick={() => onNavigate('evaluation')}>
            🎯 View ML Evaluation
          </button>
        </div>
      </div>
    </div>
  );
}

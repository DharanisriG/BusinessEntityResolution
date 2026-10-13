import React from 'react';

export default function Statistics({ stats }) {
  if (!stats) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
        Loading statistics and charts...
      </div>
    );
  }

  const totalPairs = stats.potential_matches || 1;
  const matchCount = (stats.match_status_breakdown && stats.match_status_breakdown['Resolved Matches']) || stats.high_confidence_matches || 0;
  const potentialCount = (stats.match_status_breakdown && stats.match_status_breakdown['Potential Matches']) || 0;
  const nonMatchCount = (stats.match_status_breakdown && stats.match_status_breakdown['Non-Matches']) || 0;
  const reviewCount = (stats.match_status_breakdown && stats.match_status_breakdown['Requires Review']) || 0;

  const dedupRate = stats.total_records > 0 ? ((stats.duplicate_records / stats.total_records) * 100).toFixed(1) : '0.0';

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Analytics & Statistics</h1>
          <p className="page-subtitle">
            Quantitative analysis of entity deduplication rate, confidence tier distribution, and multi-source coverage.
          </p>
        </div>
      </div>

      {/* Top Highlight Summary Cards */}
      <div className="stats-grid">
        <div className="stat-card" style={{ '--card-accent': '#6366F1' }}>
          <div className="stat-label">Total Ingested Records</div>
          <div className="stat-value">{stats.total_records}</div>
          <div className="stat-desc">Across all ingested source tables</div>
        </div>

        <div className="stat-card" style={{ '--card-accent': '#10B981' }}>
          <div className="stat-label">Resolved Master Entities</div>
          <div className="stat-value">{stats.unique_entities}</div>
          <div className="stat-desc">Unique real-world businesses</div>
        </div>

        <div className="stat-card" style={{ '--card-accent': '#8B5CF6' }}>
          <div className="stat-label">Duplicates Removed</div>
          <div className="stat-value">{stats.duplicate_records}</div>
          <div className="stat-desc">{dedupRate}% reduction in redundancy</div>
        </div>

        <div className="stat-card" style={{ '--card-accent': '#06B6D4' }}>
          <div className="stat-label">High Confidence Matches</div>
          <div className="stat-value">{stats.high_confidence_matches}</div>
          <div className="stat-desc">Pairs with score ≥ 75%</div>
        </div>
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        
        {/* Chart 1: Confidence Distribution */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '0.4rem' }}>
            📊 Confidence Tier Distribution
          </h2>
          <div className="card-desc" style={{ marginBottom: '1.25rem' }}>
            Breakdown of candidate pair scores across 5 resolution confidence bands
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
            {Object.entries(stats.confidence_distribution || {}).map(([tier, count]) => {
              const allPairsSum = Object.values(stats.confidence_distribution).reduce((a, b) => a + b, 0) || 1;
              const pct = ((count / allPairsSum) * 100).toFixed(1);
              
              let color = '#6366F1';
              if (tier.includes('Very High')) color = '#10B981';
              else if (tier.includes('High')) color = '#06B6D4';
              else if (tier.includes('Possible')) color = '#F59E0B';
              else if (tier.includes('Low')) color = '#F97316';
              else color = '#64748B';

              return (
                <div key={tier}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.35rem' }}>
                    <span style={{ fontWeight: 600, color: '#f1f5f9' }}>{tier}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', color: '#94a3b8' }}>
                      {count} ({pct}%)
                    </span>
                  </div>
                  <div className="confidence-bar-bg" style={{ height: '8px' }}>
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${Math.min(100, parseFloat(pct) * 1.5 || (count > 0 ? 4 : 0))}%`, backgroundColor: color }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Chart 2: Source Records Breakdown */}
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '0.4rem' }}>
            🏢 Records Ingested Per Source
          </h2>
          <div className="card-desc" style={{ marginBottom: '1.25rem' }}>
            Distribution of input records contributed by each source system
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {Object.entries(stats.records_per_source || {}).map(([src, count]) => {
              const pct = ((count / Math.max(1, stats.total_records)) * 100).toFixed(1);
              return (
                <div key={src} style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                    <span style={{ fontWeight: 700, color: '#fff', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="badge badge-source">{src}</span>
                    </span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#38bdf8' }}>
                      {count} records ({pct}%)
                    </span>
                  </div>
                  <div className="confidence-bar-bg" style={{ height: '8px' }}>
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${pct}%`, backgroundColor: '#38BDF8' }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Resolution Pipeline Efficiency Card */}
      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>
          ⚙️ Resolution System Performance Indicators
        </h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1.25rem' }}>
          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              Consolidation Ratio
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#34D399', fontFamily: 'var(--font-mono)' }}>
              {stats.unique_entities ? (stats.total_records / stats.unique_entities).toFixed(2) : 1} : 1
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.3rem' }}>
              Average records consolidated per unique entity
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              High-Precision Match Rate
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#38BDF8', fontFamily: 'var(--font-mono)' }}>
              {stats.potential_matches ? ((stats.high_confidence_matches / stats.potential_matches) * 100).toFixed(1) : 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.3rem' }}>
              Percentage of candidate pairs classified as high confidence
            </div>
          </div>

          <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1.25rem', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
              Deduplication Yield
            </div>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#A78BFA', fontFamily: 'var(--font-mono)' }}>
              {stats.duplicate_records} Records
            </div>
            <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.3rem' }}>
              Redundant copies eliminated from the master index
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

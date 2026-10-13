import React, { useState, useEffect } from 'react';
import { fetchPairwiseResults, getExportResultsUrl, reviewMatch } from '../api';

export default function MatchTable() {
  const [results, setResults] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [limit] = useState(15);
  
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [tierFilter, setTierFilter] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [reviewMsg, setReviewMsg] = useState('');
  
  // Explainability Modal State
  const [selectedPair, setSelectedPair] = useState(null);

  const loadResults = async () => {
    setIsLoading(true);
    try {
      const data = await fetchPairwiseResults({
        search,
        status: statusFilter,
        tier: tierFilter,
        page,
        limit
      });
      setResults(data.results || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching results:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadResults();
  }, [page, statusFilter, tierFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadResults();
  };

  const handleReviewAction = async (pair, action) => {
    try {
      await reviewMatch(pair.record_id_1, pair.record_id_2, action);
      setReviewMsg(`Successfully marked (${pair.record_id_1} ↔ ${pair.record_id_2}) as ${action === 'confirm' ? 'Confirmed Match' : 'Rejected Non-Match'}`);
      if (selectedPair) {
        setSelectedPair({
          ...selectedPair,
          status: action === 'confirm' ? 'Match' : 'Non-Match',
          tier: action === 'confirm' ? 'Manually Confirmed' : 'Manually Rejected',
          is_match: action === 'confirm'
        });
      }
      setTimeout(() => setReviewMsg(''), 4000);
      loadResults();
    } catch (err) {
      console.error('Failed to submit review action:', err);
    }
  };

  const getStatusBadgeClass = (status) => {
    if (status === 'Match') return 'badge-match';
    if (status === 'Potential Match') return 'badge-potential';
    return 'badge-review';
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10B981';
    if (score >= 75) return '#06B6D4';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Candidate Match Results</h1>
          <p className="page-subtitle">
            Explore pairwise comparisons generated across sources. Each pair is classified by the Machine Learning model with detailed attribute similarity explainability.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', flexWrap: 'wrap' }}>
          <a
            href={getExportResultsUrl('csv', statusFilter)}
            download="matched_pairs.csv"
            className="btn btn-secondary btn-sm"
          >
            📥 Export CSV
          </a>
          <a
            href={getExportResultsUrl('json', statusFilter)}
            download="matched_pairs.json"
            className="btn btn-secondary btn-sm"
          >
            📥 Export JSON
          </a>
          <span className="badge badge-source" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
            Total Pairs Evaluated: {total.toLocaleString()}
          </span>
        </div>
      </div>

      {reviewMsg && (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#6ee7b7', padding: '0.8rem 1.2rem', borderRadius: '8px', marginBottom: '1.25rem' }}>
          ✓ {reviewMsg}
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="card" style={{ padding: '1rem 1.25rem', marginBottom: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 260px' }}>
            <input
              type="text"
              className="input-control"
              placeholder="Search by business name or record ID..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ minWidth: '180px' }}>
            <select
              className="input-control"
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Statuses</option>
              <option value="Match">Match</option>
              <option value="Potential Match">Potential Match</option>
              <option value="Review Required">Review Required</option>
              <option value="Non-Match">Non-Match</option>
            </select>
          </div>

          <div style={{ minWidth: '180px' }}>
            <select
              className="input-control"
              value={tierFilter}
              onChange={(e) => { setTierFilter(e.target.value); setPage(1); }}
            >
              <option value="">All Confidence Tiers</option>
              <option value="Very High">Very High Confidence (90-100%)</option>
              <option value="High">High Confidence (75-89%)</option>
              <option value="Possible">Possible Match (60-74%)</option>
              <option value="Low">Low Confidence (40-59%)</option>
              <option value="Unlikely">Unlikely Match (0-39%)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-sm">
            🔍 Search
          </button>
          
          {(search || statusFilter || tierFilter) && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => { setSearch(''); setStatusFilter(''); setTierFilter(''); setPage(1); }}
            >
              ✕ Reset
            </button>
          )}
        </form>
      </div>

      {/* Matches Table */}
      <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
        <div className="table-container" style={{ border: 'none' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Record 1 (Source)</th>
                <th>Record 2 (Source)</th>
                <th>Confidence Score</th>
                <th>Decision Tier</th>
                <th>Status</th>
                <th>Explainability</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                    Loading matches...
                  </td>
                </tr>
              ) : results.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
                    No matching pairs found matching your criteria.
                  </td>
                </tr>
              ) : (
                results.map((pair, idx) => {
                  const scoreColor = getScoreColor(pair.confidence_score);
                  return (
                    <tr key={idx}>
                      <td>
                        <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '2px' }}>
                          {pair.business_name_1}
                        </div>
                        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                          <span className="mono">{pair.record_id_1}</span>
                          <span className="badge badge-source" style={{ fontSize: '0.7rem' }}>{pair.source_1}</span>
                        </div>
                      </td>

                      <td>
                        <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '2px' }}>
                          {pair.business_name_2}
                        </div>
                        <div style={{ display: 'flex', gap: '0.4rem', alignItems: 'center' }}>
                          <span className="mono">{pair.record_id_2}</span>
                          <span className="badge badge-source" style={{ fontSize: '0.7rem' }}>{pair.source_2}</span>
                        </div>
                      </td>

                      <td style={{ minWidth: '160px' }}>
                        <div className="confidence-bar-wrapper">
                          <div className="confidence-bar-bg">
                            <div
                              className="confidence-bar-fill"
                              style={{
                                width: `${pair.confidence_score}%`,
                                backgroundColor: scoreColor
                              }}
                            />
                          </div>
                          <span className="confidence-text" style={{ color: scoreColor }}>
                            {pair.confidence_score.toFixed(1)}%
                          </span>
                        </div>
                      </td>

                      <td>
                        <span style={{ fontSize: '0.82rem', color: '#cbd5e1', fontWeight: 500 }}>
                          {pair.tier}
                        </span>
                      </td>

                      <td>
                        <span className={`badge ${getStatusBadgeClass(pair.status)}`}>
                          {pair.status}
                        </span>
                      </td>

                      <td>
                        <div style={{ display: 'flex', gap: '0.35rem', alignItems: 'center' }}>
                          <button
                            className="btn btn-secondary btn-sm"
                            onClick={() => setSelectedPair(pair)}
                            title="View feature similarity breakdown and evidence"
                          >
                            🔍 Explain
                          </button>
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ color: '#34d399', borderColor: 'rgba(16, 185, 129, 0.3)', padding: '0.4rem 0.6rem' }}
                            onClick={() => handleReviewAction(pair, 'confirm')}
                            title="Manually Confirm Match"
                          >
                            ✓
                          </button>
                          <button
                            className="btn btn-secondary btn-sm"
                            style={{ color: '#f87171', borderColor: 'rgba(239, 68, 68, 0.3)', padding: '0.4rem 0.6rem' }}
                            onClick={() => handleReviewAction(pair, 'reject')}
                            title="Manually Reject Match"
                          >
                            ✗
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 1.25rem', borderTop: '1px solid var(--border-subtle)' }}>
          <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
            Showing page <strong style={{ color: '#fff' }}>{page}</strong> of <strong style={{ color: '#fff' }}>{totalPages}</strong> ({total} total pairs)
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1 || isLoading}
            >
              ← Previous
            </button>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || isLoading}
            >
              Next →
            </button>
          </div>
        </div>
      </div>

      {/* Explainability Modal */}
      {selectedPair && (
        <div className="modal-overlay" onClick={() => setSelectedPair(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h2 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff' }}>
                  Match Explainability & Evidence
                </h2>
                <div style={{ fontSize: '0.82rem', color: '#94a3b8' }}>
                  Detailed feature breakdown for candidate pair ({selectedPair.record_id_1} ↔ {selectedPair.record_id_2})
                </div>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedPair(null)}
                style={{ borderRadius: '50%', width: '32px', height: '32px', padding: 0 }}
              >
                ✕
              </button>
            </div>

            {/* Compared Records Box */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                  {selectedPair.source_1} ({selectedPair.record_id_1})
                </div>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f8fafc' }}>
                  {selectedPair.business_name_1}
                </div>
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.8)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', marginBottom: '0.3rem' }}>
                  {selectedPair.source_2} ({selectedPair.record_id_2})
                </div>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f8fafc' }}>
                  {selectedPair.business_name_2}
                </div>
              </div>
            </div>

            {/* Overall Score Badge */}
            <div style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid var(--border-active)', padding: '1rem 1.25rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <div style={{ fontSize: '0.8rem', color: '#a5b4fc', textTransform: 'uppercase', fontWeight: 600 }}>
                  Consensus Match Confidence
                </div>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#fff' }}>
                  {selectedPair.confidence_score.toFixed(1)}%
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className={`badge ${getStatusBadgeClass(selectedPair.status)}`} style={{ fontSize: '0.9rem', padding: '6px 14px' }}>
                  {selectedPair.status}
                </span>
                <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '0.3rem' }}>
                  Tier: {selectedPair.tier}
                </div>
              </div>
            </div>

            {/* Similarity Breakdown Bars */}
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
              Attribute Similarities:
            </h3>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '0.85rem', marginBottom: '1.5rem' }}>
              {selectedPair.similarity_breakdown && [
                { label: 'Business Name', val: selectedPair.similarity_breakdown.business_name_similarity },
                { label: 'Address / Street', val: selectedPair.similarity_breakdown.address_similarity },
                { label: 'Phone Number', val: selectedPair.similarity_breakdown.phone_similarity },
                { label: 'Email Address', val: selectedPair.similarity_breakdown.email_similarity },
                { label: 'Website / Domain', val: selectedPair.similarity_breakdown.website_similarity },
                { label: 'City Match', val: selectedPair.similarity_breakdown.city_similarity },
              ].map((item, i) => (
                <div key={i} style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '0.3rem' }}>
                    <span style={{ color: '#cbd5e1' }}>{item.label}</span>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: getScoreColor(item.val) }}>
                      {item.val}%
                    </span>
                  </div>
                  <div className="confidence-bar-bg">
                    <div
                      className="confidence-bar-fill"
                      style={{ width: `${item.val}%`, backgroundColor: getScoreColor(item.val) }}
                    />
                  </div>
                </div>
              ))}
            </div>

            {/* Evidence Summary List */}
            <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
              Matching Evidence & Logic:
            </h3>
            <ul style={{ paddingLeft: '1.25rem', color: '#94a3b8', fontSize: '0.85rem', lineHeight: '1.6' }}>
              {selectedPair.evidence_summary && selectedPair.evidence_summary.map((ev, i) => (
                <li key={i} style={{ color: '#cbd5e1' }}>{ev}</li>
              ))}
            </ul>

            {/* Modal Actions */}
            <div style={{ marginTop: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '1rem' }}>
              <div style={{ display: 'flex', gap: '0.6rem' }}>
                <button
                  className="btn btn-sm"
                  style={{ background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', border: '1px solid rgba(16, 185, 129, 0.4)' }}
                  onClick={() => handleReviewAction(selectedPair, 'confirm')}
                >
                  ✓ Confirm Match
                </button>
                <button
                  className="btn btn-sm"
                  style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#f87171', border: '1px solid rgba(239, 68, 68, 0.4)' }}
                  onClick={() => handleReviewAction(selectedPair, 'reject')}
                >
                  ✗ Reject Match
                </button>
              </div>
              <button className="btn btn-primary btn-sm" onClick={() => setSelectedPair(null)}>
                Close Evidence
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

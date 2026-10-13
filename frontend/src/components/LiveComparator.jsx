import React, { useState } from 'react';
import { compareRecords } from '../api';

const PRESETS = [
  {
    title: 'Legal Suffix & Abbreviation Variation',
    desc: 'Same business with Pvt Ltd vs Private Limited, missing dot in URL, case difference',
    rec1: {
      source_record_id: 'PRE_A1',
      business_name: 'Apex Technology Solutions Pvt. Ltd.',
      address: '100 Market St, Ste 500',
      city: 'San Francisco',
      state: 'CA',
      country: 'USA',
      phone: '+1 (415) 123-4567',
      email: 'contact@apextech.com',
      website: 'https://www.apextech.com'
    },
    rec2: {
      source_record_id: 'PRE_A2',
      business_name: 'apex technology solutions private limited',
      address: '100 Market Street #500',
      city: 'San Francisco',
      state: 'California',
      country: 'USA',
      phone: '4151234567',
      email: 'info@apextech.com',
      website: 'http://apextech.com'
    }
  },
  {
    title: 'Typo in Name & Street Abbreviation',
    desc: 'Slight typographical error in company name and abbreviated street address',
    rec1: {
      source_record_id: 'PRE_B1',
      business_name: 'Beacon Financial Advisory Inc.',
      address: '238 Tech Parkway, Suite 792',
      city: 'New York',
      state: 'NY',
      country: 'USA',
      phone: '+1 212 958 9935',
      email: 'contact@beaconfa.com',
      website: 'https://www.beaconfa.com'
    },
    rec2: {
      source_record_id: 'PRE_B2',
      business_name: 'Becon Financial Advisory',
      address: '238 Tech Pkwy Ste 792',
      city: 'New York',
      state: 'NY',
      country: 'USA',
      phone: '(212) 958-9935',
      email: 'advisory@beaconfa.com',
      website: 'www.beaconfa.com'
    }
  },
  {
    title: 'Distinct Companies in Same City',
    desc: 'Different entities operating in the same metropolitan area (True Negative non-match)',
    rec1: {
      source_record_id: 'PRE_C1',
      business_name: 'Cascade Global Logistics',
      address: '99 Brigade Rd',
      city: 'Seattle',
      state: 'WA',
      country: 'USA',
      phone: '+1 206 295 4582',
      email: 'support@cascadelogistics.com',
      website: 'https://www.cascadelogistics.com'
    },
    rec2: {
      source_record_id: 'PRE_C2',
      business_name: 'Evergreen Renewable Energy',
      address: '450 Pine Street',
      city: 'Seattle',
      state: 'WA',
      country: 'USA',
      phone: '+1 206 883 1290',
      email: 'info@evergreenenergy.org',
      website: 'https://www.evergreenenergy.org'
    }
  }
];

export default function LiveComparator() {
  const [rec1, setRec1] = useState(PRESETS[0].rec1);
  const [rec2, setRec2] = useState(PRESETS[0].rec2);
  const [threshold, setThreshold] = useState(60.0);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleApplyPreset = (preset) => {
    setRec1(preset.rec1);
    setRec2(preset.rec2);
    setResult(null);
    setErrorMsg('');
  };

  const handleCompare = async (e) => {
    if (e) e.preventDefault();
    if (!rec1.business_name || !rec2.business_name) {
      setErrorMsg('Please enter a business name for both records.');
      return;
    }

    setIsLoading(true);
    setErrorMsg('');
    try {
      const data = await compareRecords(rec1, rec2, threshold);
      setResult(data);
    } catch (err) {
      setErrorMsg(err.message || 'Failed to compare records');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 90) return '#10B981';
    if (score >= 75) return '#06B6D4';
    if (score >= 60) return '#F59E0B';
    return '#EF4444';
  };

  const getStatusBadgeClass = (status) => {
    if (status === 'Match') return 'badge-match';
    if (status === 'Potential Match') return 'badge-potential';
    return 'badge-review';
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Live Entity Resolution Sandbox</h1>
          <p className="page-subtitle">
            Test and visualize the real-time record linkage pipeline on arbitrary custom business profiles.
            Inspect field normalizations, pairwise string similarities, and ML RandomForest classifications on the fly.
          </p>
        </div>
      </div>

      {/* Presets Bar */}
      <div className="card" style={{ padding: '1rem 1.25rem', marginBottom: '1.5rem' }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', marginBottom: '0.6rem' }}>
          💡 Quick Test Benchmark Presets:
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleApplyPreset(p)}
              title={p.desc}
            >
              Preset {idx + 1}: {p.title}
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', padding: '0.9rem 1.2rem', borderRadius: '8px', marginBottom: '1.5rem' }}>
          ⚠️ {errorMsg}
        </div>
      )}

      {/* Side-by-Side Input Forms */}
      <form onSubmit={handleCompare}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
          
          {/* Record 1 Form */}
          <div className="card" style={{ borderLeft: '4px solid #6366F1' }}>
            <div className="card-header">
              <span className="card-title">🏢 Record A (Source 1)</span>
              <span className="badge badge-source">Candidate Record A</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Business Name *</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="e.g. Apex Technology Solutions Pvt Ltd"
                  value={rec1.business_name}
                  onChange={(e) => setRec1({ ...rec1, business_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Street Address</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="e.g. 100 Market St, Ste 500"
                  value={rec1.address}
                  onChange={(e) => setRec1({ ...rec1, address: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>City</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="San Francisco"
                    value={rec1.city}
                    onChange={(e) => setRec1({ ...rec1, city: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>State</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="CA"
                    value={rec1.state}
                    onChange={(e) => setRec1({ ...rec1, state: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Country</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="USA"
                    value={rec1.country}
                    onChange={(e) => setRec1({ ...rec1, country: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Phone</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="+1 (415) 123-4567"
                  value={rec1.phone}
                  onChange={(e) => setRec1({ ...rec1, phone: e.target.value })}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Email</label>
                <input
                  type="email"
                  className="input-control"
                  placeholder="contact@apextech.com"
                  value={rec1.email}
                  onChange={(e) => setRec1({ ...rec1, email: e.target.value })}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Website</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="https://www.apextech.com"
                  value={rec1.website}
                  onChange={(e) => setRec1({ ...rec1, website: e.target.value })}
                />
              </div>
            </div>
          </div>

          {/* Record 2 Form */}
          <div className="card" style={{ borderLeft: '4px solid #06B6D4' }}>
            <div className="card-header">
              <span className="card-title">🏢 Record B (Source 2)</span>
              <span className="badge badge-source">Candidate Record B</span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Business Name *</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="e.g. apex technology solutions private limited"
                  value={rec2.business_name}
                  onChange={(e) => setRec2({ ...rec2, business_name: e.target.value })}
                  required
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Street Address</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="e.g. 100 Market Street #500"
                  value={rec2.address}
                  onChange={(e) => setRec2({ ...rec2, address: e.target.value })}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: '0.5rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>City</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="San Francisco"
                    value={rec2.city}
                    onChange={(e) => setRec2({ ...rec2, city: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>State</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="California"
                    value={rec2.state}
                    onChange={(e) => setRec2({ ...rec2, state: e.target.value })}
                  />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Country</label>
                  <input
                    type="text"
                    className="input-control"
                    placeholder="USA"
                    value={rec2.country}
                    onChange={(e) => setRec2({ ...rec2, country: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Phone</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="(415) 123-4567"
                  value={rec2.phone}
                  onChange={(e) => setRec2({ ...rec2, phone: e.target.value })}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Email</label>
                <input
                  type="email"
                  className="input-control"
                  placeholder="info@apextech.com"
                  value={rec2.email}
                  onChange={(e) => setRec2({ ...rec2, email: e.target.value })}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Website</label>
                <input
                  type="text"
                  className="input-control"
                  placeholder="http://apextech.com"
                  value={rec2.website}
                  onChange={(e) => setRec2({ ...rec2, website: e.target.value })}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Action Button & Threshold Slider */}
        <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', padding: '1rem 1.5rem', marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: '1 1 300px' }}>
            <span style={{ fontSize: '0.85rem', color: '#cbd5e1', whiteSpace: 'nowrap' }}>
              Decision Threshold: <strong style={{ color: '#818cf8', fontFamily: 'var(--font-mono)' }}>{threshold}%</strong>
            </span>
            <input
              type="range"
              min="30"
              max="90"
              step="5"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              style={{ width: '100%', accentColor: '#6366f1', cursor: 'pointer' }}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ padding: '0.75rem 2rem', fontSize: '0.95rem' }}
            disabled={isLoading}
          >
            {isLoading ? '⚙️ Evaluating Machine Learning Features...' : '🚀 Compare & Resolve Records'}
          </button>
        </div>
      </form>

      {/* Resolution Output Card */}
      {result && result.result && (
        <div className="card" style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(19, 29, 51, 0.95))', border: '1px solid var(--border-active)', borderRadius: '12px' }}>
          
          {/* Top Score Banner */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)', marginBottom: '1.5rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Resolution Verdict & Consensus Score
              </div>
              <div style={{ fontSize: '2.4rem', fontWeight: 800, color: getScoreColor(result.result.confidence_score), fontFamily: 'var(--font-mono)', lineHeight: 1.1, marginTop: '0.2rem' }}>
                {result.result.confidence_score.toFixed(1)}%
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <span className={`badge ${getStatusBadgeClass(result.result.status)}`} style={{ fontSize: '1rem', padding: '8px 18px' }}>
                {result.result.status}
              </span>
              <div style={{ fontSize: '0.82rem', color: '#94a3b8', marginTop: '0.4rem' }}>
                Classification Tier: <strong style={{ color: '#fff' }}>{result.result.tier}</strong>
              </div>
            </div>
          </div>

          {/* Normalization Comparison */}
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
            Standardized Canonical Representations:
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', fontSize: '0.82rem' }}>
              <div style={{ fontWeight: 700, color: '#818cf8', marginBottom: '0.5rem' }}>RECORD A NORMALIZED:</div>
              <div style={{ color: '#f8fafc', marginBottom: '0.2rem' }}><strong>Name:</strong> {result.record1_normalized.norm_name || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Core:</strong> {result.record1_normalized.core_name || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Address:</strong> {result.record1_normalized.norm_address || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Phone:</strong> {result.record1_normalized.norm_phone || '—'}</div>
              <div style={{ color: '#cbd5e1' }}><strong>Email:</strong> {result.record1_normalized.norm_email || '—'}</div>
            </div>

            <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)', fontSize: '0.82rem' }}>
              <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: '0.5rem' }}>RECORD B NORMALIZED:</div>
              <div style={{ color: '#f8fafc', marginBottom: '0.2rem' }}><strong>Name:</strong> {result.record2_normalized.norm_name || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Core:</strong> {result.record2_normalized.core_name || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Address:</strong> {result.record2_normalized.norm_address || '—'}</div>
              <div style={{ color: '#cbd5e1', marginBottom: '0.2rem' }}><strong>Phone:</strong> {result.record2_normalized.norm_phone || '—'}</div>
              <div style={{ color: '#cbd5e1' }}><strong>Email:</strong> {result.record2_normalized.norm_email || '—'}</div>
            </div>
          </div>

          {/* Similarity Meters */}
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
            Pairwise Attribute Similarity Features:
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.85rem', marginBottom: '1.5rem' }}>
            {result.result.similarity_breakdown && [
              { label: 'Business Name (Token Sort)', val: result.result.similarity_breakdown.business_name_similarity },
              { label: 'Street Address', val: result.result.similarity_breakdown.address_similarity },
              { label: 'Phone Number', val: result.result.similarity_breakdown.phone_similarity },
              { label: 'Email Address', val: result.result.similarity_breakdown.email_similarity },
              { label: 'Website Domain', val: result.result.similarity_breakdown.website_similarity },
              { label: 'City / Location', val: result.result.similarity_breakdown.city_similarity }
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

          {/* Explainability Evidence Points */}
          <h3 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.5rem' }}>
            Machine Learning Resolution Evidence:
          </h3>
          <ul style={{ paddingLeft: '1.25rem', color: '#cbd5e1', fontSize: '0.85rem', lineHeight: '1.6' }}>
            {result.result.evidence_summary && result.result.evidence_summary.map((ev, i) => (
              <li key={i}>{ev}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

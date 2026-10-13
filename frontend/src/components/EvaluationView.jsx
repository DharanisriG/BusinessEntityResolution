import React, { useState, useEffect } from 'react';
import { fetchEvaluation } from '../api';

export default function EvaluationView() {
  const [datasetSplit, setDatasetSplit] = useState('test');
  const [threshold, setThreshold] = useState(60.0);
  const [evalData, setEvalData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const loadEvaluation = async () => {
    setIsLoading(true);
    try {
      const data = await fetchEvaluation({ dataset: datasetSplit, threshold });
      setEvalData(data);
    } catch (err) {
      console.error('Error fetching evaluation:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvaluation();
  }, [datasetSplit, threshold]);

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Machine Learning Model Evaluation</h1>
          <p className="page-subtitle">
            Ground-truth validation metrics for the Entity Resolution Machine Learning classifier (Random Forest with 15 pairwise similarity features).
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', background: 'rgba(15, 23, 42, 0.8)', padding: '4px 8px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>Dataset:</span>
            <button
              className={`btn btn-sm ${datasetSplit === 'test' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setDatasetSplit('test')}
            >
              Test Split (Unseen)
            </button>
            <button
              className={`btn btn-sm ${datasetSplit === 'train' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setDatasetSplit('train')}
            >
              Train Split
            </button>
          </div>
        </div>
      </div>

      {isLoading || !evalData ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Computing evaluation metrics against ground-truth pairs...
        </div>
      ) : (
        <div>
          {/* Top Metric Cards */}
          <div className="stats-grid">
            <div className="stat-card" style={{ '--card-accent': '#10B981' }}>
              <div className="stat-label">Model Accuracy</div>
              <div className="stat-value">{evalData.metrics.accuracy}%</div>
              <div className="stat-desc">Overall pairwise classification accuracy</div>
            </div>

            <div className="stat-card" style={{ '--card-accent': '#06B6D4' }}>
              <div className="stat-label">Precision (Match)</div>
              <div className="stat-value">{evalData.metrics.precision}%</div>
              <div className="stat-desc">Predicted matches that are true entities</div>
            </div>

            <div className="stat-card" style={{ '--card-accent': '#6366F1' }}>
              <div className="stat-label">Recall (Sensitivity)</div>
              <div className="stat-value">{evalData.metrics.recall}%</div>
              <div className="stat-desc">True duplicate pairs correctly captured</div>
            </div>

            <div className="stat-card" style={{ '--card-accent': '#8B5CF6' }}>
              <div className="stat-label">F1-Score</div>
              <div className="stat-value">{evalData.metrics.f1_score}%</div>
              <div className="stat-desc">Harmonic mean of precision and recall</div>
            </div>
          </div>

          {/* Confusion Matrix and Threshold Curve Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
            
            {/* Confusion Matrix Card */}
            <div className="card">
              <h2 className="card-title" style={{ marginBottom: '0.4rem' }}>
                🎯 Confusion Matrix Breakdown
              </h2>
              <div className="card-desc" style={{ marginBottom: '1.25rem' }}>
                Contingency table of actual vs predicted record pair classifications
              </div>

              <div style={{ background: 'rgba(15, 23, 42, 0.7)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border-subtle)' }}>
                <div className="cm-grid">
                  <div></div>
                  <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: '0.78rem' }}>PREDICTED NON-MATCH</div>
                  <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: '0.78rem' }}>PREDICTED MATCH</div>

                  <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: '0.78rem', textAlign: 'left' }}>ACTUAL NON-MATCH</div>
                  <div className="cm-cell cm-tn">
                    <span style={{ fontSize: '1.4rem' }}>{evalData.metrics.true_negatives}</span>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>True Negative (TN)</span>
                  </div>
                  <div className="cm-cell cm-fp">
                    <span style={{ fontSize: '1.4rem' }}>{evalData.metrics.false_positives}</span>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>False Positive (FP)</span>
                  </div>

                  <div style={{ fontWeight: 700, color: '#94a3b8', fontSize: '0.78rem', textAlign: 'left' }}>ACTUAL MATCH</div>
                  <div className="cm-cell cm-fn">
                    <span style={{ fontSize: '1.4rem' }}>{evalData.metrics.false_negatives}</span>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>False Negative (FN)</span>
                  </div>
                  <div className="cm-cell cm-tp">
                    <span style={{ fontSize: '1.4rem' }}>{evalData.metrics.true_positives}</span>
                    <span style={{ fontSize: '0.72rem', textTransform: 'uppercase' }}>True Positive (TP)</span>
                  </div>
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginTop: '1rem', fontSize: '0.82rem' }}>
                <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
                  <strong style={{ color: '#34d399' }}>✓ Correct Classifications: </strong>
                  <span style={{ color: '#f8fafc', fontWeight: 700 }}>
                    {evalData.metrics.true_positives + evalData.metrics.true_negatives} pairs
                  </span>
                </div>
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                  <strong style={{ color: '#f87171' }}>✗ Misclassifications: </strong>
                  <span style={{ color: '#f8fafc', fontWeight: 700 }}>
                    {evalData.metrics.false_positives + evalData.metrics.false_negatives} pairs
                  </span>
                </div>
              </div>
            </div>

            {/* Threshold Sensitivity & Trade-Off Table */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h2 className="card-title">Precision-Recall Tradeoff Curve</h2>
                  <div className="card-desc">Effect of decision threshold on performance metrics</div>
                </div>
              </div>

              <div className="table-container" style={{ marginBottom: '1rem' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Threshold</th>
                      <th>Precision</th>
                      <th>Recall</th>
                      <th>F1-Score</th>
                    </tr>
                  </thead>
                  <tbody>
                    {evalData.threshold_analysis && evalData.threshold_analysis.map((row) => (
                      <tr
                        key={row.threshold}
                        style={{
                          background: row.threshold === threshold ? 'rgba(99, 102, 241, 0.18)' : 'transparent',
                          fontWeight: row.threshold === threshold ? 700 : 400
                        }}
                      >
                        <td>
                          <span className="mono" style={{ color: row.threshold === threshold ? '#a5b4fc' : '#cbd5e1' }}>
                            ≥ {row.threshold}% {row.threshold === threshold ? '★ Active' : ''}
                          </span>
                        </td>
                        <td style={{ color: '#38bdf8' }}>{row.precision}%</td>
                        <td style={{ color: '#34d399' }}>{row.recall}%</td>
                        <td style={{ color: '#a78bfa', fontWeight: 700 }}>{row.f1_score}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Threshold Slider Control */}
              <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#e2e8f0', fontWeight: 600 }}>Adjust Active Decision Threshold:</span>
                  <span style={{ fontFamily: 'var(--font-mono)', color: '#818cf8', fontWeight: 700 }}>
                    {threshold}%
                  </span>
                </div>
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
            </div>
          </div>

          {/* Academic / Viva Explanation Banner */}
          <div className="card" style={{ borderLeft: '4px solid #6366F1' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.4rem' }}>
              📘 Entity Resolution Tradeoff Explanation
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
              {evalData.tradeoff_explanation}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

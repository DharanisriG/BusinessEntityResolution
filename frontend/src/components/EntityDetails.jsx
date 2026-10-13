import React, { useState, useEffect } from 'react';
import { fetchEntities, fetchEntityDetails, getExportEntitiesUrl } from '../api';

export default function EntityDetails() {
  const [entities, setEntities] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [page, setPage] = useState(1);
  const [limit] = useState(12);

  const [search, setSearch] = useState('');
  const [hasDuplicatesFilter, setHasDuplicatesFilter] = useState(null); // true, false, or null
  const [isLoading, setIsLoading] = useState(true);

  // Drilldown Modal
  const [selectedEntity, setSelectedEntity] = useState(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  const loadEntities = async () => {
    setIsLoading(true);
    try {
      const data = await fetchEntities({
        search,
        has_duplicates: hasDuplicatesFilter,
        page,
        limit
      });
      setEntities(data.entities || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Error fetching entities:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEntities();
  }, [page, hasDuplicatesFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(1);
    loadEntities();
  };

  const handleOpenDetail = async (entityId) => {
    setLoadingDetail(true);
    try {
      const detail = await fetchEntityDetails(entityId);
      setSelectedEntity(detail);
    } catch (err) {
      console.error('Error loading entity detail:', err);
    } finally {
      setLoadingDetail(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Canonical Business Entities</h1>
          <p className="page-subtitle">
            Resolved master entity profiles synthesized from multiple noisy source records.
            Click any entity to inspect its canonical fields, linked source records tree, and deduplication evidence.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <a
            href={getExportEntitiesUrl('csv', hasDuplicatesFilter)}
            download="canonical_entities.csv"
            className="btn btn-secondary btn-sm"
          >
            📥 Export CSV
          </a>
          <a
            href={getExportEntitiesUrl('json', hasDuplicatesFilter)}
            download="canonical_entities.json"
            className="btn btn-secondary btn-sm"
          >
            📥 Export JSON
          </a>
          <span className="badge badge-match" style={{ fontSize: '0.85rem', padding: '6px 12px' }}>
            Unique Master Entities: {total}
          </span>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="card" style={{ padding: '1rem 1.25rem', marginBottom: '1.25rem' }}>
        <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: '1 1 280px' }}>
            <input
              type="text"
              className="input-control"
              placeholder="Search by entity name, ID, city, email..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          <div style={{ minWidth: '200px' }}>
            <select
              className="input-control"
              value={hasDuplicatesFilter === null ? '' : hasDuplicatesFilter.toString()}
              onChange={(e) => {
                const val = e.target.value;
                setHasDuplicatesFilter(val === '' ? null : val === 'true');
                setPage(1);
              }}
            >
              <option value="">All Entities (Master & Singletons)</option>
              <option value="true">Only Consolidated (≥ 2 Records)</option>
              <option value="false">Singletons (1 Record Only)</option>
            </select>
          </div>

          <button type="submit" className="btn btn-primary btn-sm">
            🔍 Search
          </button>

          {(search || hasDuplicatesFilter !== null) && (
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => { setSearch(''); setHasDuplicatesFilter(null); setPage(1); }}
            >
              ✕ Reset
            </button>
          )}
        </form>
      </div>

      {/* Entity Cards Grid */}
      {isLoading ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          Loading resolved business entities...
        </div>
      ) : entities.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>
          No entities found matching search query.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
          {entities.map((ent) => (
            <div
              key={ent.entity_id}
              className="card"
              style={{
                cursor: 'pointer',
                margin: 0,
                transition: 'all 0.2s ease',
                borderLeft: ent.duplicate_count > 0 ? '4px solid #6366F1' : '4px solid #64748B'
              }}
              onClick={() => handleOpenDetail(ent.entity_id)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.6rem' }}>
                <span className="mono" style={{ fontSize: '0.78rem', background: 'rgba(255,255,255,0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                  {ent.entity_id}
                </span>
                <span className={`badge ${ent.duplicate_count > 0 ? 'badge-match' : 'badge-source'}`}>
                  {ent.records_count} {ent.records_count === 1 ? 'Record' : 'Records Linked'}
                </span>
              </div>

              <h2 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.6rem', lineHeight: 1.3 }}>
                {ent.canonical_name}
              </h2>

              <div style={{ fontSize: '0.82rem', color: '#cbd5e1', display: 'flex', flexDirection: 'column', gap: '0.3rem', marginBottom: '0.9rem' }}>
                {ent.city && (
                  <div>📍 {ent.city}{ent.state ? `, ${ent.state}` : ''}{ent.country ? ` (${ent.country.toUpperCase()})` : ''}</div>
                )}
                {ent.phone && <div>📞 {ent.phone}</div>}
                {ent.email && <div>✉️ {ent.email}</div>}
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '0.75rem', borderTop: '1px solid var(--border-subtle)' }}>
                <div style={{ display: 'flex', gap: '0.3rem' }}>
                  {ent.sources && ent.sources.map((s, i) => (
                    <span key={i} className="badge badge-source" style={{ fontSize: '0.68rem' }}>{s}</span>
                  ))}
                </div>
                <span style={{ fontSize: '0.8rem', color: '#818cf8', fontWeight: 600 }}>
                  Inspect Details →
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '1rem 0' }}>
        <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
          Page <strong style={{ color: '#fff' }}>{page}</strong> of <strong style={{ color: '#fff' }}>{totalPages}</strong> ({total} total entities)
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

      {/* Drilldown Canonical Entity Modal */}
      {selectedEntity && (
        <div className="modal-overlay" onClick={() => setSelectedEntity(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <span className="mono" style={{ background: 'rgba(99, 102, 241, 0.2)', color: '#a5b4fc', padding: '2px 8px', borderRadius: '4px', fontWeight: 700 }}>
                    {selectedEntity.entity_id}
                  </span>
                  <span className="badge badge-match">
                    {selectedEntity.records_count} Source Records Merged
                  </span>
                </div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#fff', marginTop: '0.35rem' }}>
                  {selectedEntity.canonical_name}
                </h2>
              </div>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setSelectedEntity(null)}
                style={{ borderRadius: '50%', width: '32px', height: '32px', padding: 0 }}
              >
                ✕
              </button>
            </div>

            {/* Canonical Master Profile Card */}
            <div style={{ background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.9), rgba(19, 29, 51, 0.9))', border: '1px solid var(--border-active)', borderRadius: '12px', padding: '1.25rem', marginBottom: '1.5rem' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#818cf8', textTransform: 'uppercase', marginBottom: '0.75rem', letterSpacing: '0.05em' }}>
                🌟 Golden Record / Canonical Attributes
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>ADDRESS</div>
                  <div style={{ color: '#f8fafc', fontWeight: 600 }}>{selectedEntity.address || '—'}</div>
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>LOCATION</div>
                  <div style={{ color: '#f8fafc', fontWeight: 600 }}>
                    {[selectedEntity.city, selectedEntity.state, selectedEntity.country].filter(Boolean).join(', ') || '—'}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>PHONE</div>
                  <div style={{ color: '#f8fafc', fontWeight: 600 }}>{selectedEntity.phone || '—'}</div>
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>EMAIL</div>
                  <div style={{ color: '#f8fafc', fontWeight: 600 }}>{selectedEntity.email || '—'}</div>
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>WEBSITE</div>
                  <div style={{ color: '#f8fafc', fontWeight: 600 }}>{selectedEntity.website || '—'}</div>
                </div>
                <div>
                  <div style={{ color: '#64748b', fontSize: '0.75rem' }}>RESOLUTION CONFIDENCE</div>
                  <div style={{ color: '#34d399', fontWeight: 700 }}>{selectedEntity.confidence}%</div>
                </div>
              </div>
            </div>

            {/* Tree Hierarchy Diagram */}
            <div style={{ marginBottom: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                Entity Resolution Hierarchy Tree
              </h3>
              
              <div className="entity-tree-node">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 800, color: '#ffffff' }}>
                    🏢 Master Entity: {selectedEntity.canonical_name}
                  </span>
                  <span className="badge badge-match">{selectedEntity.entity_id}</span>
                </div>
              </div>

              {selectedEntity.records && selectedEntity.records.map((rec, i) => (
                <div key={i} className="entity-tree-node entity-tree-child">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="badge badge-source">{rec.source || `Source ${i+1}`}</span>
                      <span className="mono" style={{ color: '#93c5fd' }}>{rec.source_record_id}</span>
                    </div>
                    <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Linked Record #{i+1}</span>
                  </div>

                  <div style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.3rem' }}>
                    {rec.business_name}
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', fontSize: '0.78rem', color: '#94a3b8' }}>
                    {rec.address && <span>📍 {rec.address}</span>}
                    {rec.phone && <span>📞 {rec.phone}</span>}
                    {rec.email && <span>✉️ {rec.email}</span>}
                    {rec.website && <span>🌐 {rec.website}</span>}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ textAlign: 'right', marginTop: '1.5rem' }}>
              <button className="btn btn-primary btn-sm" onClick={() => setSelectedEntity(null)}>
                Close Entity Profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * API Client for Business Entity Resolution Backend.
 */

const API_BASE = '';

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to fetch backend health status');
  return res.json();
}

export async function fetchStatistics() {
  const res = await fetch(`${API_BASE}/statistics`);
  if (!res.ok) throw new Error('Failed to fetch dashboard statistics');
  return res.json();
}

export async function fetchEntities({ search = '', source = '', has_duplicates = null, page = 1, limit = 20 } = {}) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (source) params.append('source', source);
  if (has_duplicates !== null) params.append('has_duplicates', has_duplicates);
  params.append('page', page);
  params.append('limit', limit);

  const res = await fetch(`${API_BASE}/entities?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch resolved entities');
  return res.json();
}

export async function fetchEntityDetails(entityId) {
  const res = await fetch(`${API_BASE}/entities/${encodeURIComponent(entityId)}`);
  if (!res.ok) throw new Error(`Failed to fetch entity details for ${entityId}`);
  return res.json();
}

export async function fetchPairwiseResults({ search = '', tier = '', status = '', page = 1, limit = 25 } = {}) {
  const params = new URLSearchParams();
  if (search) params.append('search', search);
  if (tier) params.append('tier', tier);
  if (status) params.append('status', status);
  params.append('page', page);
  params.append('limit', limit);

  const res = await fetch(`${API_BASE}/results?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch matching results');
  return res.json();
}

export async function fetchEvaluation({ dataset = 'test', threshold = 60.0 } = {}) {
  const params = new URLSearchParams();
  params.append('dataset', dataset);
  params.append('threshold', threshold);

  const res = await fetch(`${API_BASE}/evaluation?${params.toString()}`);
  if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
  return res.json();
}

export async function triggerMatching({ threshold = 60.0, use_blocking = true, dataset_type = 'train' } = {}) {
  const res = await fetch(`${API_BASE}/match`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ threshold, use_blocking, dataset_type })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to execute entity resolution');
  }
  return res.json();
}

export async function uploadSourceFiles(formData) {
  const res = await fetch(`${API_BASE}/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to upload dataset files');
  }
  return res.json();
}

export async function compareRecords(record1, record2, threshold = 60.0) {
  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ record1, record2, threshold })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to compare records');
  }
  return res.json();
}

export async function reviewMatch(recordId1, recordId2, action) {
  const res = await fetch(`${API_BASE}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ record_id_1: recordId1, record_id_2: recordId2, action })
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to submit review action');
  }
  return res.json();
}

export function getExportEntitiesUrl(format = 'csv', has_duplicates = null) {
  const params = new URLSearchParams();
  params.append('format', format);
  if (has_duplicates !== null) params.append('has_duplicates', has_duplicates);
  return `${API_BASE}/export/entities?${params.toString()}`;
}

export function getExportResultsUrl(format = 'csv', status = '') {
  const params = new URLSearchParams();
  params.append('format', format);
  if (status) params.append('status', status);
  return `${API_BASE}/export/results?${params.toString()}`;
}


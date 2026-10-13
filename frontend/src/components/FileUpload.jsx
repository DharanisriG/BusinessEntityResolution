import React, { useState } from 'react';
import { uploadSourceFiles, triggerMatching } from '../api';

export default function FileUpload({ onResolutionComplete }) {
  const [source1File, setSource1File] = useState(null);
  const [source2File, setSource2File] = useState(null);
  const [source3File, setSource3File] = useState(null);
  
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Handle file input changes
  const handleFileSelect = (sourceKey, file) => {
    if (sourceKey === 1) setSource1File(file);
    if (sourceKey === 2) setSource2File(file);
    if (sourceKey === 3) setSource3File(file);
    setErrorMsg('');
    setSuccessMsg('');
  };

  // Submit uploaded files
  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!source1File && !source2File && !source3File) {
      setErrorMsg('Please select at least one .tsv or .csv file to upload.');
      return;
    }

    setIsUploading(true);
    setErrorMsg('');
    setSuccessMsg('');

    try {
      const formData = new FormData();
      if (source1File) formData.append('source1', source1File);
      if (source2File) formData.append('source2', source2File);
      if (source3File) formData.append('source3', source3File);

      const res = await uploadSourceFiles(formData);
      setUploadStatus(res);
      setSuccessMsg(res.message || 'Dataset uploaded and processed successfully!');
      if (onResolutionComplete) onResolutionComplete();
    } catch (err) {
      setErrorMsg(err.message || 'Error uploading dataset files');
    } finally {
      setIsUploading(false);
    }
  };

  // Quick load synthetic pre-built dataset
  const handleLoadDatasetSplit = async (datasetType) => {
    setIsUploading(true);
    setErrorMsg('');
    setSuccessMsg('');
    try {
      const res = await triggerMatching({ dataset_type: datasetType, threshold: 60.0 });
      setSuccessMsg(`Successfully loaded and resolved ${datasetType.toUpperCase()} dataset (${res.unique_entities_found} unique entities resolved)!`);
      if (onResolutionComplete) onResolutionComplete();
    } catch (err) {
      setErrorMsg(err.message || `Failed to load ${datasetType} dataset`);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1 className="page-title">Dataset Management & Ingestion</h1>
          <p className="page-subtitle">
            Upload custom multi-source business data files in TSV or CSV format, or switch between pre-configured benchmark datasets.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handleLoadDatasetSplit('train')}
            disabled={isUploading}
          >
            🔄 Load Benchmark Train Set
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => handleLoadDatasetSplit('test')}
            disabled={isUploading}
          >
            🔄 Load Benchmark Test Set
          </button>
        </div>
      </div>

      {/* Notifications */}
      {errorMsg && (
        <div style={{ background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#fca5a5', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span>⚠️</span>
          <span>{errorMsg}</span>
        </div>
      )}

      {successMsg && (
        <div style={{ background: 'rgba(16, 185, 129, 0.15)', border: '1px solid rgba(16, 185, 129, 0.3)', color: '#6ee7b7', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <span>✅</span>
          <span>{successMsg}</span>
        </div>
      )}

      {/* File Upload Cards Grid */}
      <form onSubmit={handleUploadSubmit}>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
          
          {/* Source 1 Upload Card */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Source 1 Dataset</span>
              <span className="badge badge-source">Required / Primary</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '1rem' }}>
              Upload primary source table (.tsv or .csv format)
            </p>
            <div className="upload-zone" onClick={() => document.getElementById('source1-input').click()}>
              <input
                id="source1-input"
                type="file"
                accept=".tsv,.csv,.txt"
                style={{ display: 'none' }}
                onChange={(e) => handleFileSelect(1, e.target.files[0])}
              />
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📄</div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                {source1File ? source1File.name : 'Click to select Source 1 file'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                {source1File ? `${(source1File.size / 1024).toFixed(1)} KB` : 'Supports TSV, CSV'}
              </div>
            </div>
          </div>

          {/* Source 2 Upload Card */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Source 2 Dataset</span>
              <span className="badge badge-source">Cross-Source</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '1rem' }}>
              Upload secondary comparison source table
            </p>
            <div className="upload-zone" onClick={() => document.getElementById('source2-input').click()}>
              <input
                id="source2-input"
                type="file"
                accept=".tsv,.csv,.txt"
                style={{ display: 'none' }}
                onChange={(e) => handleFileSelect(2, e.target.files[0])}
              />
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📄</div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                {source2File ? source2File.name : 'Click to select Source 2 file'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                {source2File ? `${(source2File.size / 1024).toFixed(1)} KB` : 'Supports TSV, CSV'}
              </div>
            </div>
          </div>

          {/* Source 3 Upload Card */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Source 3 Dataset</span>
              <span className="badge badge-source">Optional Source</span>
            </div>
            <p style={{ fontSize: '0.82rem', color: '#94a3b8', marginBottom: '1rem' }}>
              Upload tertiary vendor/partner data table
            </p>
            <div className="upload-zone" onClick={() => document.getElementById('source3-input').click()}>
              <input
                id="source3-input"
                type="file"
                accept=".tsv,.csv,.txt"
                style={{ display: 'none' }}
                onChange={(e) => handleFileSelect(3, e.target.files[0])}
              />
              <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>📄</div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#f8fafc' }}>
                {source3File ? source3File.name : 'Click to select Source 3 file'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '0.3rem' }}>
                {source3File ? `${(source3File.size / 1024).toFixed(1)} KB` : 'Supports TSV, CSV'}
              </div>
            </div>
          </div>
        </div>

        {/* Action Button */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem' }}>
          <button
            type="submit"
            className="btn btn-primary"
            style={{ padding: '0.85rem 2.5rem', fontSize: '1rem' }}
            disabled={isUploading || (!source1File && !source2File && !source3File)}
          >
            {isUploading ? '⚙️ Processing & Matching...' : '🚀 Run Entity Resolution'}
          </button>
        </div>
      </form>

      {/* Upload Details Table if available */}
      {uploadStatus && uploadStatus.sources_summary && (
        <div className="card">
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Ingested Sources Summary</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Source Name</th>
                  <th>Filename</th>
                  <th>Records Detected</th>
                  <th>Columns Detected</th>
                  <th>Validation Status</th>
                </tr>
              </thead>
              <tbody>
                {uploadStatus.sources_summary.map((src, i) => (
                  <tr key={i}>
                    <td><strong>{src.source_name}</strong></td>
                    <td className="mono">{src.filename}</td>
                    <td><span className="badge badge-source">{src.record_count} rows</span></td>
                    <td style={{ fontSize: '0.78rem', color: '#cbd5e1' }}>
                      {src.columns_detected.join(', ')}
                    </td>
                    <td>
                      <span className="badge badge-match">✓ Validated</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

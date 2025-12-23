import { useEffect, useState } from 'react';
import { ingestionAPI } from '../api/services';

function Dashboard({ connections }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadStats = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await ingestionAPI.getCollectionStats();
      setStats(response.data.stats);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  const connectionCount = Object.keys(connections).length;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">
          Overview of all data sources and vector database statistics
        </p>
      </div>

      <div className="section">
        <h2 className="section-title">Active Connections</h2>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{connectionCount}</div>
            <div className="stat-label">Total Connections</div>
          </div>
          {connections.confluence && (
            <div className="stat-card">
              <div className="stat-value">✓</div>
              <div className="stat-label">Confluence</div>
            </div>
          )}
          {connections.gdrive && (
            <div className="stat-card">
              <div className="stat-value">✓</div>
              <div className="stat-label">Google Drive</div>
            </div>
          )}
          {connections.jira && (
            <div className="stat-card">
              <div className="stat-value">✓</div>
              <div className="stat-label">JIRA</div>
            </div>
          )}
          {connections.sharepoint && (
            <div className="stat-card">
              <div className="stat-value">✓</div>
              <div className="stat-label">SharePoint</div>
            </div>
          )}
          {connections.local_pdf && (
            <div className="stat-card">
              <div className="stat-value">✓</div>
              <div className="stat-label">Local PDF</div>
            </div>
          )}
        </div>

        {connectionCount === 0 && (
          <div className="card">
            <div className="empty-state">
              <div className="empty-state-icon">🔌</div>
              <div className="empty-state-text">No connections yet</div>
              <p>Connect to a data source to get started</p>
            </div>
          </div>
        )}
      </div>

      <div className="section">
        <h2 className="section-title">Vector Database Statistics</h2>
        {loading && (
          <div className="card">
            <div style={{ textAlign: 'center', padding: '24px' }}>
              <div className="loading"></div>
              <p>Loading statistics...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="alert alert-error">
            Error loading statistics: {error}
          </div>
        )}

        {stats && (
          <div className="grid grid-2">
            {Object.entries(stats).map(([collectionName, collectionStats]) => (
              <div key={collectionName} className="card">
                <h3 style={{ marginBottom: '16px', fontSize: '18px', fontWeight: '600' }}>
                  {collectionName}
                </h3>
                <div className="stats-grid">
                  <div className="stat-card">
                    <div className="stat-value">{collectionStats.total_vectors?.toLocaleString() || 0}</div>
                    <div className="stat-label">Total Vectors</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">{collectionStats.vector_size || 'N/A'}</div>
                    <div className="stat-label">Vector Size</div>
                  </div>
                </div>
                {collectionStats.status && (
                  <div style={{ marginTop: '12px' }}>
                    <span className={`badge badge-${collectionStats.status === 'green' ? 'success' : 'warning'}`}>
                      Status: {collectionStats.status}
                    </span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {!loading && !error && !stats && (
          <div className="card">
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <div className="empty-state-text">No statistics available</div>
            </div>
          </div>
        )}
      </div>

      <div className="section">
        <h2 className="section-title">Quick Actions</h2>
        <div className="grid grid-3">
          <div className="card" style={{ textAlign: 'center' }}>
            <h3 style={{ marginBottom: '12px' }}>Connect Data Sources</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Link your Confluence, JIRA, Google Drive, SharePoint, or local PDFs
            </p>
            <button className="btn btn-primary" onClick={() => window.location.href = '/confluence'}>
              Get Started
            </button>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <h3 style={{ marginBottom: '12px' }}>Browse Files</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Search and list files from connected data sources
            </p>
            <button className="btn btn-secondary" disabled={connectionCount === 0}>
              Browse Now
            </button>
          </div>
          <div className="card" style={{ textAlign: 'center' }}>
            <h3 style={{ marginBottom: '12px' }}>Ingest to Vector DB</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
              Process and ingest documents into the vector database
            </p>
            <button 
              className="btn btn-success" 
              disabled={connectionCount === 0}
              onClick={() => window.location.href = '/ingestion'}
            >
              Start Ingestion
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

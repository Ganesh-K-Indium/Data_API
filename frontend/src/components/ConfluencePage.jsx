import { useState } from 'react';
import { confluenceAPI } from '../api/services';

function ConfluencePage({ connection, onConnect }) {
  const [config, setConfig] = useState({
    url: '',
    username: '',
    api_token: '',
    cloud: true
  });
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [spaces, setSpaces] = useState([]);
  const [selectedSpace, setSelectedSpace] = useState(null);
  const [pages, setPages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPages, setSelectedPages] = useState([]);
  const [ingesting, setIngesting] = useState(false);

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    setError(null);
    try {
      const response = await confluenceAPI.connect(config);
      onConnect(response.data.connection_id, response.data.metadata);
      alert('Successfully connected to Confluence!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setConnecting(false);
    }
  };

  const loadSpaces = async () => {
    if (!connection) return;
    setLoading(true);
    try {
      const response = await confluenceAPI.listSpaces(connection.connectionId);
      setSpaces(response.data.spaces);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadPages = async (spaceKey) => {
    if (!connection) return;
    setLoading(true);
    setSelectedSpace(spaceKey);
    setSelectedPages([]);
    try {
      const response = await confluenceAPI.listPages(connection.connectionId, spaceKey);
      setPages(response.data.files);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!connection || !searchQuery) return;
    setLoading(true);
    try {
      const response = await confluenceAPI.searchPages(
        connection.connectionId, 
        searchQuery, 
        selectedSpace
      );
      setPages(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const togglePageSelection = (pageId) => {
    setSelectedPages(prev => 
      prev.includes(pageId) 
        ? prev.filter(id => id !== pageId)
        : [...prev, pageId]
    );
  };

  const selectAll = () => {
    setSelectedPages(pages.map(p => p.id));
  };

  const clearSelection = () => {
    setSelectedPages([]);
  };

  const handleIngest = async () => {
    if (selectedPages.length === 0) {
      alert('Please select at least one page to ingest');
      return;
    }
    
    setIngesting(true);
    setError(null);
    try {
      const response = await confluenceAPI.ingest(connection.connectionId, selectedPages);
      const { data } = response;
      
      const successCount = data.progress.filter(p => p.status === 'completed').length;
      const failCount = data.progress.filter(p => p.status === 'failed').length;
      
      alert(`Ingestion completed!\nSuccess: ${successCount}\nFailed: ${failCount}`);
      clearSelection();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">📝 Confluence</h1>
        <p className="page-description">
          Connect to Confluence and browse your spaces and pages
        </p>
      </div>

      {!connection ? (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Connect to Confluence</h2>
          <form onSubmit={handleConnect}>
            <div className="input-group">
              <label>Confluence URL *</label>
              <input
                type="url"
                value={config.url}
                onChange={(e) => setConfig({...config, url: e.target.value})}
                placeholder="https://your-domain.atlassian.net"
                required
              />
            </div>
            <div className="input-group">
              <label>Username/Email *</label>
              <input
                type="email"
                value={config.username}
                onChange={(e) => setConfig({...config, username: e.target.value})}
                placeholder="your-email@example.com"
                required
              />
            </div>
            <div className="input-group">
              <label>API Token *</label>
              <input
                type="password"
                value={config.api_token}
                onChange={(e) => setConfig({...config, api_token: e.target.value})}
                placeholder="Enter your Confluence API token"
                required
              />
            </div>
            <div className="checkbox-wrapper" style={{ marginBottom: '16px' }}>
              <input
                type="checkbox"
                checked={config.cloud}
                onChange={(e) => setConfig({...config, cloud: e.target.checked})}
                id="cloud-checkbox"
              />
              <label htmlFor="cloud-checkbox">Cloud Instance</label>
            </div>
            {error && <div className="alert alert-error">{error}</div>}
            <button type="submit" className="btn btn-primary" disabled={connecting}>
              {connecting ? <><div className="loading"></div> Connecting...</> : 'Connect'}
            </button>
          </form>
        </div>
      ) : (
        <>
          <div className="alert alert-success">
            ✓ Connected to Confluence (Connection ID: {connection.connectionId})
          </div>

          <div className="section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 className="section-title" style={{ marginBottom: 0 }}>Spaces</h2>
              <button className="btn btn-primary btn-sm" onClick={loadSpaces} disabled={loading}>
                {loading ? 'Loading...' : 'Load Spaces'}
              </button>
            </div>
            
            {spaces.length > 0 && (
              <div className="grid grid-3">
                {spaces.map((space) => (
                  <div 
                    key={space.id} 
                    className="card" 
                    style={{ cursor: 'pointer', border: selectedSpace === space.key ? '2px solid var(--primary-color)' : undefined }}
                    onClick={() => loadPages(space.key)}
                  >
                    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{space.name}</h3>
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Key: {space.key}</p>
                    {space.type && (
                      <span className="badge badge-info" style={{ marginTop: '8px' }}>{space.type}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedSpace && (
            <div className="section">
              <h2 className="section-title">Pages in {selectedSpace}</h2>
              
              <form onSubmit={handleSearch} className="search-bar">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search pages..."
                />
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  🔍 Search
                </button>
              </form>

              {pages.length > 0 && (
                <div style={{ marginBottom: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <button className="btn btn-sm btn-secondary" onClick={selectAll}>
                    Select All ({pages.length})
                  </button>
                  {selectedPages.length > 0 && (
                    <>
                      <button className="btn btn-sm btn-secondary" onClick={clearSelection}>
                        Clear ({selectedPages.length})
                      </button>
                      <button 
                        className="btn btn-sm btn-primary" 
                        onClick={handleIngest}
                        disabled={ingesting}
                      >
                        {ingesting ? <><div className="loading"></div> Ingesting...</> : `📥 Ingest ${selectedPages.length} Page(s)`}
                      </button>
                    </>
                  )}
                </div>
              )}

              {loading ? (
                <div style={{ textAlign: 'center', padding: '24px' }}>
                  <div className="loading"></div>
                  <p>Loading pages...</p>
                </div>
              ) : pages.length > 0 ? (
                <div className="file-list">
                  {pages.map((page) => (
                    <div key={page.id} className="file-item" style={{ cursor: 'pointer' }} onClick={() => togglePageSelection(page.id)}>
                      <div className="file-item-info">
                        <input
                          type="checkbox"
                          checked={selectedPages.includes(page.id)}
                          onChange={() => togglePageSelection(page.id)}
                          onClick={(e) => e.stopPropagation()}
                          style={{ marginRight: '12px', cursor: 'pointer' }}
                        />
                        <div className="file-item-icon">📄</div>
                        <div className="file-item-details">
                          <h4>{page.name || page.title}</h4>
                          <p>ID: {page.id}</p>
                        </div>
                      </div>
                      <div className="file-item-actions">
                        <span className="badge badge-info">{page.type || 'page'}</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">📄</div>
                  <div className="empty-state-text">No pages found</div>
                </div>
              )}
              
              {error && <div className="alert alert-error" style={{ marginTop: '16px' }}>{error}</div>}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default ConfluencePage;

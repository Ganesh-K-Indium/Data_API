import { useState } from 'react';
import { sharepointAPI } from '../api/services';

function SharePointPage({ connection, onConnect }) {
  const [config, setConfig] = useState({
    site_url: '',
    client_id: '',
    client_secret: '',
    tenant_id: ''
  });
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [sites, setSites] = useState([]);
  const [libraries, setLibraries] = useState([]);
  const [selectedSite, setSelectedSite] = useState(null);
  const [selectedLibrary, setSelectedLibrary] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [ingesting, setIngesting] = useState(false);

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    setError(null);
    try {
      const response = await sharepointAPI.connect(config);
      onConnect(response.data.connection_id, response.data.metadata);
      
      // Auto-load sites after connection
      const sitesResponse = await sharepointAPI.listSites(response.data.connection_id);
      setSites(sitesResponse.data.sites);
      
      alert('Successfully connected to SharePoint!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setConnecting(false);
    }
  };

  const loadSites = async () => {
    if (!connection) return;
    setLoading(true);
    try {
      const response = await sharepointAPI.listSites(connection.connectionId);
      setSites(response.data.sites);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadLibraries = async (siteId) => {
    if (!connection) return;
    setLoading(true);
    setSelectedSite(siteId);
    try {
      const response = await sharepointAPI.listLibraries(connection.connectionId, siteId);
      setLibraries(response.data.libraries);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadFiles = async (libraryName) => {
    if (!connection) return;
    setLoading(true);
    setSelectedLibrary(libraryName);
    setSelectedFiles([]);
    try {
      const response = await sharepointAPI.listFiles(connection.connectionId, libraryName);
      setFiles(response.data.files);
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
      const response = await sharepointAPI.searchFiles(
        connection.connectionId,
        searchQuery,
        selectedLibrary
      );
      setFiles(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleFileSelection = (fileId) => {
    setSelectedFiles(prev => 
      prev.includes(fileId) 
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  const selectAll = () => {
    setSelectedFiles(files.map(f => f.id));
  };

  const clearSelection = () => {
    setSelectedFiles([]);
  };

  const handleIngest = async () => {
    if (selectedFiles.length === 0) {
      alert('Please select at least one file to ingest');
      return;
    }
    
    setIngesting(true);
    setError(null);
    try {
      const response = await sharepointAPI.ingest(connection.connectionId, selectedFiles);
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
        <h1 className="page-title">📚 SharePoint</h1>
        <p className="page-description">
          Connect to SharePoint and browse your sites and documents
        </p>
      </div>

      {!connection ? (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Connect to SharePoint</h2>
          <form onSubmit={handleConnect}>
            <div className="input-group">
              <label>Site URL *</label>
              <input
                type="url"
                value={config.site_url}
                onChange={(e) => setConfig({...config, site_url: e.target.value})}
                placeholder="https://yourcompany.sharepoint.com/sites/yoursite"
                required
              />
            </div>
            <div className="input-group">
              <label>Client ID *</label>
              <input
                type="text"
                value={config.client_id}
                onChange={(e) => setConfig({...config, client_id: e.target.value})}
                placeholder="Azure AD Application Client ID"
                required
              />
            </div>
            <div className="input-group">
              <label>Client Secret *</label>
              <input
                type="password"
                value={config.client_secret}
                onChange={(e) => setConfig({...config, client_secret: e.target.value})}
                placeholder="Azure AD Application Client Secret"
                required
              />
            </div>
            <div className="input-group">
              <label>Tenant ID *</label>
              <input
                type="text"
                value={config.tenant_id}
                onChange={(e) => setConfig({...config, tenant_id: e.target.value})}
                placeholder="Azure AD Tenant ID"
                required
              />
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
            ✓ Connected to SharePoint (Connection ID: {connection.connectionId})
          </div>

          <div className="section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 className="section-title" style={{ marginBottom: 0 }}>Sites</h2>
              <button className="btn btn-primary btn-sm" onClick={loadSites} disabled={loading}>
                {loading ? 'Loading...' : 'Load Sites'}
              </button>
            </div>

            {sites.length > 0 && (
              <div className="grid grid-3">
                {sites.map((site, idx) => (
                  <div
                    key={idx}
                    className="card"
                    style={{ cursor: 'pointer', border: selectedSite === site.id ? '2px solid var(--primary-color)' : undefined }}
                    onClick={() => loadLibraries(site.id)}
                  >
                    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{site.name}</h3>
                    {site.webUrl && (
                      <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', wordBreak: 'break-all' }}>
                        {site.webUrl}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {libraries.length > 0 && (
            <div className="section">
              <h2 className="section-title">Document Libraries</h2>
              <div className="grid grid-3">
                {libraries.map((library, idx) => (
                  <div
                    key={idx}
                    className="card"
                    style={{ cursor: 'pointer', border: selectedLibrary === library.name ? '2px solid var(--primary-color)' : undefined }}
                    onClick={() => loadFiles(library.name)}
                  >
                    <div style={{ fontSize: '32px', marginBottom: '8px' }}>📚</div>
                    <h4 style={{ fontSize: '14px' }}>{library.name}</h4>
                  </div>
                ))}
              </div>
            </div>
          )}

          {selectedLibrary && (
            <div className="section">
              <h2 className="section-title">Files</h2>

              <form onSubmit={handleSearch} className="search-bar">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search files..."
                />
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  🔍 Search
                </button>
              </form>

              {files.length > 0 && (
                <div style={{ marginBottom: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
                  <button className="btn btn-sm btn-secondary" onClick={selectAll}>
                    Select All ({files.length})
                  </button>
                  {selectedFiles.length > 0 && (
                    <>
                      <button className="btn btn-sm btn-secondary" onClick={clearSelection}>
                        Clear ({selectedFiles.length})
                      </button>
                      <button 
                        className="btn btn-sm btn-primary" 
                        onClick={handleIngest}
                        disabled={ingesting}
                      >
                        {ingesting ? <><div className="loading"></div> Ingesting...</> : `📥 Ingest ${selectedFiles.length} File(s)`}
                      </button>
                    </>
                  )}
                </div>
              )}

              {loading ? (
                <div style={{ textAlign: 'center', padding: '24px' }}>
                  <div className="loading"></div>
                  <p>Loading files...</p>
                </div>
              ) : files.length > 0 ? (
                <div className="file-list">
                  {files.map((file) => (
                    <div key={file.id} className="file-item" style={{ cursor: 'pointer' }} onClick={() => toggleFileSelection(file.id)}>
                      <div className="file-item-info">
                        <input
                          type="checkbox"
                          checked={selectedFiles.includes(file.id)}
                          onChange={() => toggleFileSelection(file.id)}
                          onClick={(e) => e.stopPropagation()}
                          style={{ marginRight: '12px', cursor: 'pointer' }}
                        />
                        <div className="file-item-icon">
                          {file.name?.endsWith('.pdf') ? '📕' :
                           file.name?.endsWith('.docx') ? '📘' :
                           file.name?.endsWith('.xlsx') ? '📊' : '📄'}
                        </div>
                        <div className="file-item-details">
                          <h4>{file.name}</h4>
                          <p>
                            {file.size && `Size: ${(file.size / 1024).toFixed(2)} KB`}
                            {file.modified_date && ` • Modified: ${file.modified_date}`}
                          </p>
                        </div>
                      </div>
                      <div className="file-item-actions">
                        {file.type && <span className="badge badge-info">{file.type}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">📄</div>
                  <div className="empty-state-text">No files found</div>
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

export default SharePointPage;

import { useState } from 'react';
import { localPdfAPI } from '../api/services';

function LocalPdfPage({ connection, onConnect }) {
  const [config, setConfig] = useState({
    base_directory: ''
  });
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [directories, setDirectories] = useState([]);
  const [currentPath, setCurrentPath] = useState(null);
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
      const response = await localPdfAPI.connect(config);
      onConnect(response.data.connection_id, response.data.metadata);
      
      // Auto-load PDF files after connection
      const filesResponse = await localPdfAPI.listFiles(response.data.connection_id, null);
      setFiles(filesResponse.data.files);
      
      // Also load directories
      const dirsResponse = await localPdfAPI.listDirectories(response.data.connection_id, null);
      setDirectories(dirsResponse.data.directories);
      
      alert('Successfully connected to local PDF directory!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setConnecting(false);
    }
  };

  const loadDirectories = async (parentPath = null) => {
    if (!connection) return;
    setLoading(true);
    setCurrentPath(parentPath);
    try {
      const response = await localPdfAPI.listDirectories(connection.connectionId, parentPath);
      setDirectories(response.data.directories);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadFiles = async (folderPath = null) => {
    if (!connection) return;
    setLoading(true);
    setCurrentPath(folderPath);
    setSelectedFiles([]);
    try {
      const response = await localPdfAPI.listFiles(connection.connectionId, folderPath);
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
      const response = await localPdfAPI.searchFiles(
        connection.connectionId,
        searchQuery,
        currentPath
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
      alert('Please select at least one PDF to ingest');
      return;
    }
    
    setIngesting(true);
    setError(null);
    try {
      const response = await localPdfAPI.ingest(connection.connectionId, selectedFiles);
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
        <h1 className="page-title">📕 Local PDF</h1>
        <p className="page-description">
          Connect to a local directory and browse PDF files
        </p>
      </div>

      {!connection ? (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Connect to Local PDF Directory</h2>
          <form onSubmit={handleConnect}>
            <div className="input-group">
              <label>Base Directory Path *</label>
              <input
                type="text"
                value={config.base_directory}
                onChange={(e) => setConfig({...config, base_directory: e.target.value})}
                placeholder="/path/to/pdf/directory"
                required
              />
              <small style={{ color: 'var(--text-tertiary)', marginTop: '4px', display: 'block' }}>
                Enter the absolute path to the directory containing PDF files
              </small>
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
            ✓ Connected to Local PDF Directory (Connection ID: {connection.connectionId})
          </div>

          <div className="section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 className="section-title" style={{ marginBottom: 0 }}>
                Current Path: {currentPath || 'Base Directory'}
              </h2>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => loadDirectories(currentPath)}>
                  📂 Load Directories
                </button>
                <button className="btn btn-primary btn-sm" onClick={() => loadFiles(currentPath)}>
                  📕 Load PDFs
                </button>
              </div>
            </div>

            <form onSubmit={handleSearch} className="search-bar">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search PDF files..."
              />
              <button type="submit" className="btn btn-primary" disabled={loading}>
                🔍 Search
              </button>
            </form>

            {directories.length > 0 && (
              <div className="section">
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Subdirectories</h3>
                <div className="grid grid-3">
                  {directories.map((dir, idx) => (
                    <div
                      key={idx}
                      className="card"
                      style={{ cursor: 'pointer' }}
                      onClick={() => {
                        loadDirectories(dir.path || dir.name);
                        loadFiles(dir.path || dir.name);
                      }}
                    >
                      <div style={{ fontSize: '32px', marginBottom: '8px' }}>📁</div>
                      <h4 style={{ fontSize: '14px' }}>{dir.name}</h4>
                      {dir.path && (
                        <p style={{ fontSize: '12px', color: 'var(--text-tertiary)', wordBreak: 'break-all' }}>
                          {dir.path}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

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
                      {ingesting ? <><div className="loading"></div> Ingesting...</> : `📥 Ingest ${selectedFiles.length} PDF(s)`}
                    </button>
                  </>
                )}
              </div>
            )}

            {loading ? (
              <div style={{ textAlign: 'center', padding: '24px' }}>
                <div className="loading"></div>
                <p>Loading...</p>
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
                      <div className="file-item-icon">📕</div>
                      <div className="file-item-details">
                        <h4>{file.name}</h4>
                        <p>
                          {file.size && `Size: ${(file.size / 1024).toFixed(2)} KB`}
                          {file.path && ` • Path: ${file.path}`}
                        </p>
                      </div>
                    </div>
                    <div className="file-item-actions">
                      <span className="badge badge-error">PDF</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-state-icon">📕</div>
                <div className="empty-state-text">No PDF files found</div>
              </div>
            )}
            
            {error && <div className="alert alert-error" style={{ marginTop: '16px' }}>{error}</div>}
          </div>
        </>
      )}
    </div>
  );
}

export default LocalPdfPage;

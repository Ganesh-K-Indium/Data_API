import { useState } from 'react';
import { gdriveAPI } from '../api/services';

function GDrivePage({ connection, onConnect }) {
  const [config, setConfig] = useState({
    service_account_json: '',
    credentials_type: 'json_string'
  });
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [folders, setFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState('root');
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
      const response = await gdriveAPI.connect(config);
      onConnect(response.data.connection_id, response.data.metadata);
      alert('Successfully connected to Google Drive!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setConnecting(false);
    }
  };

  const loadFolders = async (parentFolder = 'root') => {
    if (!connection) return;
    setLoading(true);
    setCurrentFolder(parentFolder);
    try {
      const response = await gdriveAPI.listFolders(connection.connectionId, parentFolder);
      setFolders(response.data.folders);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadFiles = async (folderPath = 'root') => {
    if (!connection) return;
    setLoading(true);
    setCurrentFolder(folderPath);
    setSelectedFiles([]);
    try {
      const response = await gdriveAPI.listFiles(connection.connectionId, folderPath);
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
      const response = await gdriveAPI.searchFiles(
        connection.connectionId,
        searchQuery,
        currentFolder !== 'root' ? currentFolder : null
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
      const response = await gdriveAPI.ingest(connection.connectionId, selectedFiles);
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
        <h1 className="page-title">📁 Google Drive</h1>
        <p className="page-description">
          Connect to Google Drive and browse your files
        </p>
      </div>

      {!connection ? (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Connect to Google Drive</h2>
          <form onSubmit={handleConnect}>
            <div className="input-group">
              <label>Credentials Type *</label>
              <select
                value={config.credentials_type}
                onChange={(e) => setConfig({...config, credentials_type: e.target.value})}
              >
                <option value="json_string">JSON String</option>
                <option value="file_path">File Path</option>
              </select>
            </div>
            <div className="input-group">
              <label>Service Account JSON *</label>
              <textarea
                rows={8}
                value={config.service_account_json}
                onChange={(e) => setConfig({...config, service_account_json: e.target.value})}
                placeholder={config.credentials_type === 'json_string' ? 
                  'Paste your service account JSON content here...' :
                  'Enter the file path to your service account JSON'
                }
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
            ✓ Connected to Google Drive (Connection ID: {connection.connectionId})
          </div>

          <div className="section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 className="section-title" style={{ marginBottom: 0 }}>
                Current Location: {currentFolder}
              </h2>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="btn btn-secondary btn-sm" onClick={() => loadFolders(currentFolder)}>
                  📂 Load Folders
                </button>
                <button className="btn btn-primary btn-sm" onClick={() => loadFiles(currentFolder)}>
                  📄 Load Files
                </button>
              </div>
            </div>

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

            {folders.length > 0 && (
              <div className="section">
                <h3 style={{ fontSize: '16px', marginBottom: '12px' }}>Folders</h3>
                <div className="grid grid-3">
                  {folders.map((folder, idx) => (
                    <div
                      key={idx}
                      className="card"
                      style={{ cursor: 'pointer' }}
                      onClick={() => {
                        loadFolders(folder.name);
                        loadFiles(folder.name);
                      }}
                    >
                      <div style={{ fontSize: '32px', marginBottom: '8px' }}>📁</div>
                      <h4 style={{ fontSize: '14px' }}>{folder.name}</h4>
                      {folder.id && <p style={{ fontSize: '12px', color: 'var(--text-tertiary)' }}>ID: {folder.id}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {files.length > 0 && (
              <div style={{ marginBottom: '16px', marginTop: '16px', display: 'flex', gap: '12px', alignItems: 'center' }}>
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
                      <div className="file-item-icon">
                        {file.type?.includes('pdf') ? '📕' :
                         file.type?.includes('doc') ? '📘' :
                         file.type?.includes('sheet') ? '📊' : '📄'}
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
        </>
      )}
    </div>
  );
}

export default GDrivePage;

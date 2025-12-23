import { useState } from 'react';
import { jiraAPI } from '../api/services';

function JiraPage({ connection, onConnect }) {
  const [config, setConfig] = useState({
    url: '',
    username: '',
    api_token: '',
    cloud: true
  });
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleConnect = async (e) => {
    e.preventDefault();
    setConnecting(true);
    setError(null);
    try {
      const response = await jiraAPI.connect(config);
      onConnect(response.data.connection_id, response.data.metadata);
      alert('Successfully connected to JIRA!');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setConnecting(false);
    }
  };

  const loadProjects = async () => {
    if (!connection) return;
    setLoading(true);
    try {
      const response = await jiraAPI.listProjects(connection.connectionId);
      setProjects(response.data.projects);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadIssues = async (projectKey) => {
    if (!connection) return;
    setLoading(true);
    setSelectedProject(projectKey);
    try {
      const response = await jiraAPI.listIssues(connection.connectionId, projectKey);
      setIssues(response.data.files);
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
      const response = await jiraAPI.searchIssues(
        connection.connectionId,
        searchQuery,
        selectedProject
      );
      setIssues(response.data.results);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">🎫 JIRA</h1>
        <p className="page-description">
          Connect to JIRA and browse your projects and issues
        </p>
      </div>

      {!connection ? (
        <div className="card">
          <h2 style={{ marginBottom: '24px' }}>Connect to JIRA</h2>
          <form onSubmit={handleConnect}>
            <div className="input-group">
              <label>JIRA URL *</label>
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
                placeholder="Enter your JIRA API token"
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
            ✓ Connected to JIRA (Connection ID: {connection.connectionId})
          </div>

          <div className="section">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 className="section-title" style={{ marginBottom: 0 }}>Projects</h2>
              <button className="btn btn-primary btn-sm" onClick={loadProjects} disabled={loading}>
                {loading ? 'Loading...' : 'Load Projects'}
              </button>
            </div>

            {projects.length > 0 && (
              <div className="grid grid-3">
                {projects.map((project) => (
                  <div
                    key={project.id}
                    className="card"
                    style={{ cursor: 'pointer', border: selectedProject === project.key ? '2px solid var(--primary-color)' : undefined }}
                    onClick={() => loadIssues(project.key)}
                  >
                    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{project.name}</h3>
                    <p style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Key: {project.key}</p>
                    {project.type && (
                      <span className="badge badge-info" style={{ marginTop: '8px' }}>{project.type}</span>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {selectedProject && (
            <div className="section">
              <h2 className="section-title">Issues in {selectedProject}</h2>

              <form onSubmit={handleSearch} className="search-bar">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search issues..."
                />
                <button type="submit" className="btn btn-primary" disabled={loading}>
                  🔍 Search
                </button>
              </form>

              {loading ? (
                <div style={{ textAlign: 'center', padding: '24px' }}>
                  <div className="loading"></div>
                  <p>Loading issues...</p>
                </div>
              ) : issues.length > 0 ? (
                <div className="file-list">
                  {issues.map((issue) => (
                    <div key={issue.id} className="file-item">
                      <div className="file-item-info">
                        <div className="file-item-icon">🎫</div>
                        <div className="file-item-details">
                          <h4>{issue.name || issue.summary}</h4>
                          <p>ID: {issue.id} {issue.key && `• Key: ${issue.key}`}</p>
                        </div>
                      </div>
                      <div className="file-item-actions">
                        {issue.status && <span className="badge badge-info">{issue.status}</span>}
                        {issue.type && <span className="badge badge-warning">{issue.type}</span>}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="empty-state">
                  <div className="empty-state-icon">🎫</div>
                  <div className="empty-state-text">No issues found</div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default JiraPage;

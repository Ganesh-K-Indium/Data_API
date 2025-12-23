import { useState, useEffect } from 'react';
import { ingestionAPI } from '../api/services';

function IngestionPage({ connections }) {
  const [selectedSource, setSelectedSource] = useState('');
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [collectionName, setCollectionName] = useState('10K_vector_db');
  const [metadata, setMetadata] = useState('');
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Map connection keys to display names and types
  const sourceTypeMap = {
    confluence: { display: 'Confluence', type: 'confluence' },
    gdrive: { display: 'Google Drive', type: 'gdrive' },
    jira: { display: 'JIRA', type: 'jira' },
    sharepoint: { display: 'SharePoint', type: 'sharepoint' },
    local_pdf: { display: 'Local PDF', type: 'local_pdf' }
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    
    if (!selectedSource || selectedFiles.length === 0) {
      setError('Please select a source and at least one file');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const connection = connections[selectedSource];
      const sourceType = sourceTypeMap[selectedSource].type;
      
      let parsedMetadata = {};
      if (metadata.trim()) {
        try {
          parsedMetadata = JSON.parse(metadata);
        } catch {
          setError('Invalid JSON in metadata field');
          setLoading(false);
          return;
        }
      }

      const response = await ingestionAPI.ingestFiles(
        connection.connectionId,
        sourceType,
        selectedFiles,
        collectionName,
        parsedMetadata
      );

      setSuccess(`Ingestion job created successfully! Job ID: ${response.data.job_id}`);
      
      // Add job to list for tracking
      setJobs([...jobs, {
        id: response.data.job_id,
        source: sourceTypeMap[selectedSource].display,
        fileCount: selectedFiles.length,
        status: 'processing',
        timestamp: new Date().toISOString()
      }]);

      // Clear form
      setSelectedFiles([]);
      setMetadata('');

      // Poll for status
      pollJobStatus(response.data.job_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const pollJobStatus = async (jobId) => {
    const maxPolls = 60; // Poll for up to 5 minutes (60 * 5s)
    let polls = 0;

    const interval = setInterval(async () => {
      polls++;
      try {
        const response = await ingestionAPI.getJobStatus(jobId);
        const status = response.data;

        // Update job in list
        setJobs(prev => prev.map(job => 
          job.id === jobId ? { ...job, status: status.status, ...status } : job
        ));

        if (status.status === 'completed' || status.status === 'failed' || polls >= maxPolls) {
          clearInterval(interval);
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        clearInterval(interval);
      }
    }, 5000); // Poll every 5 seconds
  };

  const getJobStatus = async (jobId) => {
    try {
      const response = await ingestionAPI.getJobStatus(jobId);
      alert(JSON.stringify(response.data, null, 2));
    } catch (err) {
      alert('Error: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">⚡ Vector Database Ingestion</h1>
        <p className="page-description">
          Ingest files from connected data sources into the vector database
        </p>
      </div>

      {Object.keys(connections).length === 0 ? (
        <div className="card">
          <div className="alert alert-info">
            No data sources connected yet. Please connect to a data source first.
          </div>
        </div>
      ) : (
        <div className="two-column">
          <div>
            <div className="card">
              <h2 style={{ marginBottom: '24px' }}>Create Ingestion Job</h2>
              <form onSubmit={handleIngest}>
                <div className="input-group">
                  <label>Data Source *</label>
                  <select
                    value={selectedSource}
                    onChange={(e) => {
                      setSelectedSource(e.target.value);
                      setSelectedFiles([]);
                    }}
                    required
                  >
                    <option value="">Select a data source</option>
                    {Object.entries(connections).map(([key, conn]) => (
                      <option key={key} value={key}>
                        {sourceTypeMap[key]?.display || key} - {conn.connectionId.substring(0, 8)}...
                      </option>
                    ))}
                  </select>
                </div>

                <div className="input-group">
                  <label>File IDs *</label>
                  <textarea
                    rows={4}
                    value={selectedFiles.join('\n')}
                    onChange={(e) => setSelectedFiles(e.target.value.split('\n').filter(id => id.trim()))}
                    placeholder="Enter file IDs, one per line&#10;Example:&#10;file_id_1&#10;file_id_2&#10;file_id_3"
                    required
                  />
                  <small style={{ color: 'var(--text-tertiary)', marginTop: '4px', display: 'block' }}>
                    Enter one file ID per line. Get file IDs from the respective data source pages.
                  </small>
                </div>

                <div className="input-group">
                  <label>Collection Name</label>
                  <input
                    type="text"
                    value={collectionName}
                    onChange={(e) => setCollectionName(e.target.value)}
                    placeholder="10K_vector_db"
                  />
                  <small style={{ color: 'var(--text-tertiary)', marginTop: '4px', display: 'block' }}>
                    Note: Files are ingested into predefined collections (10K_vector_db for text, multimodel_vector_db for images)
                  </small>
                </div>

                <div className="input-group">
                  <label>Additional Metadata (JSON)</label>
                  <textarea
                    rows={3}
                    value={metadata}
                    onChange={(e) => setMetadata(e.target.value)}
                    placeholder='{"key": "value", "department": "engineering"}'
                  />
                </div>

                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                <button 
                  type="submit" 
                  className="btn btn-success" 
                  disabled={loading || !selectedSource || selectedFiles.length === 0}
                  style={{ width: '100%' }}
                >
                  {loading ? (
                    <>
                      <div className="loading"></div> Starting Ingestion...
                    </>
                  ) : (
                    <>⚡ Start Ingestion ({selectedFiles.length} file{selectedFiles.length !== 1 ? 's' : ''})</>
                  )}
                </button>
              </form>
            </div>
          </div>

          <div>
            <div className="card">
              <h2 style={{ marginBottom: '24px' }}>Active Connections</h2>
              {Object.entries(connections).map(([key, conn]) => (
                <div key={key} className="file-item" style={{ marginBottom: '8px' }}>
                  <div className="file-item-info">
                    <div className="file-item-icon">🔌</div>
                    <div className="file-item-details">
                      <h4>{sourceTypeMap[key]?.display || key}</h4>
                      <p>ID: {conn.connectionId.substring(0, 16)}...</p>
                    </div>
                  </div>
                  <div className="file-item-actions">
                    <span className="badge badge-success">Connected</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {jobs.length > 0 && (
        <div className="section">
          <h2 className="section-title">Ingestion Jobs</h2>
          <div className="card">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Job ID</th>
                    <th>Source</th>
                    <th>Files</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {jobs.map((job) => (
                    <tr key={job.id}>
                      <td>
                        <code style={{ fontSize: '12px' }}>
                          {job.id.substring(0, 8)}...
                        </code>
                      </td>
                      <td>{job.source}</td>
                      <td>{job.fileCount || job.total_files || 0}</td>
                      <td>
                        <span className={`badge badge-${
                          job.status === 'completed' ? 'success' :
                          job.status === 'failed' ? 'error' :
                          job.status === 'processing' ? 'warning' : 'info'
                        }`}>
                          {job.status}
                        </span>
                      </td>
                      <td>
                        {job.completed_files !== undefined && job.total_files ? (
                          <div>
                            {job.completed_files}/{job.total_files}
                            {job.failed_files > 0 && (
                              <span style={{ color: 'var(--error-color)', marginLeft: '8px' }}>
                                ({job.failed_files} failed)
                              </span>
                            )}
                          </div>
                        ) : '-'}
                      </td>
                      <td>
                        <button
                          className="btn btn-secondary btn-sm"
                          onClick={() => getJobStatus(job.id)}
                        >
                          Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      <div className="section">
        <h2 className="section-title">How It Works</h2>
        <div className="grid grid-3">
          <div className="card">
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>1️⃣</div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Select Source</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Choose a connected data source and specify the files to ingest
            </p>
          </div>
          <div className="card">
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>2️⃣</div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Process Files</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Files are processed using the proven PDF pipeline with text extraction and image handling
            </p>
          </div>
          <div className="card">
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>3️⃣</div>
            <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>Ingest to Qdrant</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
              Processed content is ingested into Qdrant vector collections for semantic search
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default IngestionPage;

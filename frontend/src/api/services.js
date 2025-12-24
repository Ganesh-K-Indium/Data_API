import apiClient from './client';

// Confluence API
export const confluenceAPI = {
  connect: (config) => 
    apiClient.post('/confluence/connect', {
      source_type: 'confluence',
      config
    }),
  
  listSpaces: (connectionId, limit = 50) =>
    apiClient.get('/confluence/spaces', { 
      params: { connection_id: connectionId, limit } 
    }),
  
  getSpaceInfo: (connectionId, spaceKey) =>
    apiClient.get(`/confluence/spaces/${spaceKey}`, {
      params: { connection_id: connectionId }
    }),
  
  listPages: (connectionId, spaceKey, limit = 50, offset = 0) =>
    apiClient.post('/confluence/list-files', {
      connection_id: connectionId,
      space_key: spaceKey,
      limit,
      offset
    }),
  
  searchPages: (connectionId, query, spaceKey = null, limit = 50) =>
    apiClient.post('/confluence/search', {
      connection_id: connectionId,
      query,
      space_key: spaceKey,
      limit
    }),
  
  ingest: (connectionId, fileIds, metadata = {}) =>
    apiClient.post('/confluence/ingest', {
      connection_id: connectionId,
      file_ids: fileIds,
      metadata
    })
};

// Google Drive API
export const gdriveAPI = {
  connect: (config) =>
    apiClient.post('/gdrive/connect', {
      source_type: 'gdrive',
      config
    }),
  
  listFolders: (connectionId, parentFolder = 'root') =>
    apiClient.get('/gdrive/folders', {
      params: { connection_id: connectionId, parent_folder_name: parentFolder }
    }),
  
  listFiles: (connectionId, folderPath = 'root', fileTypes = null, limit = 50, offset = 0) =>
    apiClient.post('/gdrive/list-files', {
      connection_id: connectionId,
      folder_path: folderPath,
      file_types: fileTypes,
      limit,
      offset
    }),
  
  searchFiles: (connectionId, query, folderPath = null, limit = 50) =>
    apiClient.post('/gdrive/search', {
      connection_id: connectionId,
      query,
      folder_path: folderPath,
      limit
    }),
  
  ingest: (connectionId, fileIds, metadata = {}) =>
    apiClient.post('/gdrive/ingest', {
      connection_id: connectionId,
      file_ids: fileIds,
      metadata
    })
};

// JIRA API
export const jiraAPI = {
  connect: (config) =>
    apiClient.post('/jira/connect', {
      source_type: 'jira',
      config
    }),
  
  listProjects: (connectionId) =>
    apiClient.get('/jira/projects', {
      params: { connection_id: connectionId }
    }),
  
  listIssues: (connectionId, projectKey = null, limit = 50, offset = 0) =>
    apiClient.post('/jira/list-files', {
      connection_id: connectionId,
      project_key: projectKey,
      limit,
      offset
    }),
  
  searchIssues: (connectionId, query, projectKey = null, limit = 50) =>
    apiClient.post('/jira/search', {
      connection_id: connectionId,
      query,
      project_key: projectKey,
      limit
    }),
  
  ingest: (connectionId, fileIds, metadata = {}) =>
    apiClient.post('/jira/ingest', {
      connection_id: connectionId,
      file_ids: fileIds,
      metadata
    })
};

// SharePoint API
export const sharepointAPI = {
  connect: (config) =>
    apiClient.post('/sharepoint/connect', {
      source_type: 'sharepoint',
      config
    }),
  
  listSites: (connectionId) =>
    apiClient.get('/sharepoint/sites', {
      params: { connection_id: connectionId }
    }),
  
  listLibraries: (connectionId, siteId = null) =>
    apiClient.get('/sharepoint/libraries', {
      params: { connection_id: connectionId, site_id: siteId }
    }),
  
  listFiles: (connectionId, libraryName = null, folderPath = null, limit = 50, offset = 0) =>
    apiClient.post('/sharepoint/list-files', {
      connection_id: connectionId,
      folder_path: libraryName || folderPath || 'Documents',
      limit,
      offset
    }),
  
  searchFiles: (connectionId, query, libraryName = null, limit = 50) =>
    apiClient.post('/sharepoint/search', {
      connection_id: connectionId,
      query,
      filters: libraryName ? { library_name: libraryName } : {},
      limit
    }),
  
  ingest: (connectionId, fileIds, metadata = {}) =>
    apiClient.post('/sharepoint/ingest', {
      connection_id: connectionId,
      file_ids: fileIds,
      metadata
    })
};

// Local PDF API
export const localPdfAPI = {
  connect: (config) =>
    apiClient.post('/local-pdf/connect', {
      source_type: 'local_pdf',
      config
    }),
  
  listDirectories: (connectionId, parentPath = null) =>
    apiClient.get('/local-pdf/directories', {
      params: { connection_id: connectionId, parent_path: parentPath }
    }),
  
  listFiles: (connectionId, folderPath = null, limit = 50, offset = 0) =>
    apiClient.post('/local-pdf/list-files', {
      connection_id: connectionId,
      folder_path: folderPath,
      limit,
      offset
    }),
  
  searchFiles: (connectionId, query, folderPath = null, limit = 50) =>
    apiClient.post('/local-pdf/search', {
      connection_id: connectionId,
      query,
      folder_path: folderPath,
      limit
    }),
  
  ingest: (connectionId, fileIds, metadata = {}) =>
    apiClient.post('/local-pdf/ingest', {
      connection_id: connectionId,
      file_ids: fileIds,
      metadata
    })
};

// Ingestion API
export const ingestionAPI = {
  ingestFiles: (connectionId, sourceType, fileIds, collectionName = '10K_vector_db', metadata = {}) =>
    apiClient.post('/ingest/', {
      connection_id: connectionId,
      source_type: sourceType,
      file_ids: fileIds,
      collection_name: collectionName,
      metadata
    }),
  
  getJobStatus: (jobId) =>
    apiClient.get(`/ingest/status/${jobId}`),
  
  getCollectionStats: () =>
    apiClient.get('/ingest/collections/stats')
};

export default {
  confluence: confluenceAPI,
  gdrive: gdriveAPI,
  jira: jiraAPI,
  sharepoint: sharepointAPI,
  localPdf: localPdfAPI,
  ingestion: ingestionAPI
};

# Data Sources REST API

A comprehensive FastAPI-based REST API server for connecting to multiple data sources and ingesting documents into vector databases. This system provides a unified interface for Confluence, Google Drive, JIRA, Local PDF files, and SharePoint.

## 🚀 Features

- **Multi-Source Support**: Connect to 5 different data sources through a unified API
- **RESTful Architecture**: Clean REST API endpoints for all operations
- **Vector Database Integration**: Automatic ingestion into Qdrant vector database
- **Connection Management**: Manage multiple active connections simultaneously
- **Flexible Configuration**: Configure via environment variables or API requests
- **Background Processing**: Asynchronous file ingestion with progress tracking
- **UI-Ready**: Designed to be easily integrated with any frontend application

## 📋 Supported Data Sources

1. **Confluence** - Atlassian Confluence Cloud/Server
2. **Google Drive** - Google Drive via Service Account
3. **JIRA** - JIRA Cloud/Server issues and projects
4. **Local PDF** - Local PDF file directories
5. **SharePoint** - Microsoft SharePoint Online

## 🏗️ Architecture

```
api_services/
├── main.py                 # FastAPI application entry point
├── config.py              # Connection management & configuration
├── models.py              # Pydantic data models
├── requirements.txt       # Python dependencies
├── services/              # Business logic layer
│   ├── confluence_service.py
│   ├── gdrive_service.py
│   ├── jira_service.py
│   ├── local_pdf_service.py
│   ├── sharepoint_service.py
│   └── vector_store_service.py
└── routers/               # API route handlers
    ├── confluence_router.py
    ├── gdrive_router.py
    ├── jira_router.py
    ├── local_pdf_router.py
    ├── sharepoint_router.py
    └── ingestion_router.py
```

## 🛠️ Installation

### Prerequisites

- Python 3.9+
- Qdrant vector database (local or cloud)
- OpenAI API key for embeddings

### Setup

1. **Clone or navigate to the directory**:
```bash
cd api_services
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**:
Create a `.env` file in the `api_services` directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# OpenAI (for embeddings)
OPENAI_API_KEY=your_openai_api_key

# Qdrant Vector Database
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # Optional for cloud

# Optional: Pre-configured data sources
# CONFLUENCE_URL=https://your-domain.atlassian.net
# CONFLUENCE_USERNAME=your_email
# CONFLUENCE_API_TOKEN=your_token

# JIRA_URL=https://your-domain.atlassian.net
# JIRA_USERNAME=your_email
# JIRA_API_TOKEN=your_token

# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# SHAREPOINT_SITE_URL=https://yourdomain.sharepoint.com/sites/yoursite
# SHAREPOINT_CLIENT_ID=your_client_id
# SHAREPOINT_CLIENT_SECRET=your_client_secret
# SHAREPOINT_TENANT_ID=your_tenant_id
```

## 🚀 Running the Server

### Development Mode

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Usage

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Connect to a Data Source

#### Confluence Example
```bash
curl -X POST http://localhost:8000/confluence/connect \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "confluence",
    "config": {
      "url": "https://your-domain.atlassian.net",
      "username": "your-email@example.com",
      "api_token": "your-api-token",
      "cloud": true
    }
  }'
```

Response:
```json
{
  "success": true,
  "message": "Successfully connected to Confluence",
  "connection_id": "confluence_a1b2c3d4",
  "metadata": {
    "source_type": "confluence",
    "status": "connected",
    "instance_url": "https://your-domain.atlassian.net"
  }
}
```

#### Google Drive Example
```bash
curl -X POST http://localhost:8000/gdrive/connect \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "gdrive",
    "config": {
      "service_account_json": "/path/to/service-account.json",
      "credentials_type": "file_path"
    }
  }'
```

### 3. List Files/Content

#### List Confluence Pages
```bash
curl -X POST http://localhost:8000/confluence/list-files \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "confluence",
    "connection_id": "confluence_a1b2c3d4",
    "space_key": "TEAM",
    "limit": 50
  }'
```

#### List Google Drive Files
```bash
curl -X POST http://localhost:8000/gdrive/list-files \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "gdrive",
    "connection_id": "gdrive_e5f6g7h8",
    "folder_path": "root",
    "file_types": ["pdf", "docx"],
    "limit": 100
  }'
```

### 4. Search Content

```bash
curl -X POST http://localhost:8000/confluence/search \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "confluence",
    "connection_id": "confluence_a1b2c3d4",
    "query": "project documentation",
    "filters": {
      "space_key": "TEAM"
    },
    "limit": 50
  }'
```

### 5. Ingest Files into Vector Database

```bash
curl -X POST http://localhost:8000/ingest/ \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "confluence",
    "connection_id": "confluence_a1b2c3d4",
    "file_ids": ["12345", "67890"],
    "collection_name": "my_knowledge_base",
    "chunk_size": 1000,
    "chunk_overlap": 200,
    "metadata": {
      "project": "documentation",
      "team": "engineering"
    }
  }'
```

Response:
```json
{
  "success": true,
  "job_id": "job_abc123def456",
  "message": "Ingestion job created for 2 files",
  "total_files": 2,
  "progress": []
}
```

### 6. Check Ingestion Status

```bash
curl http://localhost:8000/ingest/status/job_abc123def456
```

Response:
```json
{
  "job_id": "job_abc123def456",
  "status": "completed",
  "total_files": 2,
  "completed_files": 2,
  "failed_files": 0,
  "progress": [
    {
      "file_id": "12345",
      "file_name": "Project Overview",
      "status": "completed",
      "chunks_created": 15
    },
    {
      "file_id": "67890",
      "file_name": "Architecture Design",
      "status": "completed",
      "chunks_created": 23
    }
  ],
  "started_at": "2024-01-15T10:30:00",
  "completed_at": "2024-01-15T10:35:00"
}
```

### 7. Manage Connections

#### List Active Connections
```bash
curl http://localhost:8000/connections
```

#### Get Connection Status
```bash
curl http://localhost:8000/connections/confluence_a1b2c3d4
```

#### Close Connection
```bash
curl -X DELETE http://localhost:8000/connections/confluence_a1b2c3d4
```

## 🔌 Data Source Specific Endpoints

### Confluence
- `POST /confluence/connect` - Connect to Confluence
- `GET /confluence/spaces` - List spaces
- `GET /confluence/spaces/{space_key}` - Get space info
- `POST /confluence/list-files` - List pages
- `POST /confluence/search` - Search content
- `GET /confluence/pages/{page_id}` - Get page content
- `GET /confluence/pages/{page_id}/children` - Get child pages

### Google Drive
- `POST /gdrive/connect` - Connect to Google Drive
- `GET /gdrive/folders` - List folders
- `POST /gdrive/list-files` - List files
- `POST /gdrive/search` - Search files
- `GET /gdrive/files/{file_id}/metadata` - Get file metadata

### JIRA
- `POST /jira/connect` - Connect to JIRA
- `GET /jira/projects` - List projects
- `POST /jira/list-files` - List issues
- `POST /jira/search` - Search issues
- `GET /jira/issues/{issue_key}` - Get issue details

### Local PDF
- `POST /local-pdf/connect` - Connect to PDF directory
- `GET /local-pdf/directories` - List subdirectories
- `POST /local-pdf/list-files` - List PDF files
- `POST /local-pdf/search` - Search files by name

### SharePoint
- `POST /sharepoint/connect` - Connect to SharePoint
- `GET /sharepoint/sites` - List sites
- `GET /sharepoint/libraries` - List document libraries
- `POST /sharepoint/list-files` - List files
- `POST /sharepoint/search` - Search files
- `GET /sharepoint/files/{file_id}/metadata` - Get file metadata

## 🎯 Use Cases

### Frontend Integration

This API is designed to be easily integrated with any frontend application:

1. **User provides credentials** via UI form
2. **Frontend calls connect endpoint** for the chosen data source
3. **Frontend receives connection_id** to use for subsequent requests
4. **User browses/searches content** through list and search endpoints
5. **User selects files** to ingest
6. **Frontend initiates ingestion** with selected file IDs
7. **Frontend polls status endpoint** to show progress

### Example Flow

```javascript
// 1. Connect to Confluence
const connectResponse = await fetch('http://localhost:8000/confluence/connect', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    source_type: 'confluence',
    config: {
      url: userInputs.url,
      username: userInputs.username,
      api_token: userInputs.apiToken,
      cloud: true
    }
  })
});
const { connection_id } = await connectResponse.json();

// 2. List available pages
const listResponse = await fetch('http://localhost:8000/confluence/list-files', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    source_type: 'confluence',
    connection_id: connection_id,
    space_key: 'TEAM',
    limit: 100
  })
});
const { files } = await listResponse.json();

// 3. User selects files in UI, then ingest
const selectedFileIds = ['123', '456', '789'];
const ingestResponse = await fetch('http://localhost:8000/ingest/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    source_type: 'confluence',
    connection_id: connection_id,
    file_ids: selectedFileIds,
    collection_name: 'my_collection',
    chunk_size: 1000,
    chunk_overlap: 200
  })
});
const { job_id } = await ingestResponse.json();

// 4. Poll for status
const checkStatus = async () => {
  const statusResponse = await fetch(`http://localhost:8000/ingest/status/${job_id}`);
  const status = await statusResponse.json();
  
  if (status.status === 'completed') {
    console.log('Ingestion complete!');
  } else if (status.status === 'in_progress') {
    setTimeout(checkStatus, 2000); // Check again in 2 seconds
  }
};
checkStatus();
```

## 🔒 Security Considerations

1. **CORS**: Configure `allow_origins` in production to specific domains
2. **API Keys**: Never commit API keys to version control
3. **Authentication**: Consider adding API key authentication for production
4. **Rate Limiting**: Implement rate limiting for public endpoints
5. **Input Validation**: All inputs are validated via Pydantic models

## 📝 Configuration File Support

You can also pre-configure data sources via a JSON configuration file:

Create `data_sources_config.json`:
```json
{
  "sources": [
    {
      "source_type": "confluence",
      "enabled": true,
      "config": {
        "url": "https://your-domain.atlassian.net",
        "username": "your-email@example.com",
        "api_token": "your-token",
        "cloud": true
      }
    },
    {
      "source_type": "gdrive",
      "enabled": true,
      "config": {
        "service_account_json": "/path/to/service-account.json",
        "credentials_type": "file_path"
      }
    }
  ]
}
```

Set the environment variable:
```env
CONFIG_FILE=data_sources_config.json
```

## 🧪 Testing

Test the API using the interactive documentation:

1. Start the server: `python main.py`
2. Open browser: http://localhost:8000/docs
3. Try out endpoints directly in the Swagger UI

## 🐛 Troubleshooting

### Connection Issues

- Verify credentials are correct
- Check network connectivity to data sources
- Ensure service account has proper permissions (Google Drive)
- Verify API tokens are not expired

### Ingestion Issues

- Check Qdrant is running and accessible
- Verify OpenAI API key is valid
- Ensure sufficient disk space for temporary files
- Check file permissions for local PDF files

### Performance

- Use background processing for large ingestion jobs
- Adjust chunk size based on your use case
- Consider running Qdrant on separate server for production
- Use connection pooling for multiple concurrent requests

## 📊 Monitoring

The API provides several monitoring endpoints:

- `/health` - Overall system health
- `/connections` - Active connections
- `/ingest/status/{job_id}` - Ingestion job progress
- `/ingest/collections/{collection_name}/stats` - Vector DB statistics

## 🤝 Contributing

This API is designed to be modular and extensible. To add a new data source:

1. Create service file in `services/`
2. Create router file in `routers/`
3. Add client initialization in `config.py`
4. Register router in `main.py`
5. Update models as needed

## 📄 License

[Your License Here]

## 🆘 Support

For issues and questions:
- Check the interactive API docs at `/docs`
- Review the troubleshooting section
- Check connection status via `/connections` endpoint

---

**Built with FastAPI, LangChain, and Qdrant**

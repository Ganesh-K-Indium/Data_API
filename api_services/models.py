"""
Pydantic models for API requests and responses
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DataSourceType(str, Enum):
    """Supported data source types"""
    CONFLUENCE = "confluence"
    GDRIVE = "gdrive"
    JIRA = "jira"
    LOCAL_PDF = "local_pdf"
    SHAREPOINT = "sharepoint"


# ========== Configuration Models ==========
class ConfluenceConfig(BaseModel):
    """Confluence connection configuration"""
    url: str = Field(..., description="Confluence instance URL")
    username: str = Field(..., description="Confluence username/email")
    api_token: str = Field(..., description="Confluence API token")
    cloud: bool = Field(default=True, description="Is Confluence Cloud (vs Server)")


class GDriveConfig(BaseModel):
    """Google Drive connection configuration"""
    service_account_json: str = Field(..., description="Service account JSON content or file path")
    credentials_type: str = Field(default="json_string", description="Either 'json_string' or 'file_path'")


class JiraConfig(BaseModel):
    """JIRA connection configuration"""
    url: str = Field(..., description="JIRA instance URL")
    username: str = Field(..., description="JIRA username/email")
    api_token: str = Field(..., description="JIRA API token")
    cloud: bool = Field(default=True, description="Is JIRA Cloud (vs Server)")


class SharePointConfig(BaseModel):
    """SharePoint connection configuration"""
    site_url: str = Field(..., description="SharePoint site URL")
    client_id: str = Field(..., description="Azure AD client ID")
    client_secret: str = Field(..., description="Azure AD client secret")
    tenant_id: str = Field(..., description="Azure AD tenant ID")


class LocalPDFConfig(BaseModel):
    """Local PDF configuration"""
    base_directory: str = Field(..., description="Base directory for PDF files")


class DataSourceConfig(BaseModel):
    """Generic data source configuration"""
    source_type: DataSourceType
    config: Dict[str, Any] = Field(..., description="Source-specific configuration")
    enabled: bool = Field(default=True, description="Whether this source is enabled")


# ========== Connection Models ==========
class ConnectionRequest(BaseModel):
    """Request to establish connection to a data source"""
    source_type: DataSourceType
    config: Dict[str, Any]


class ConnectionResponse(BaseModel):
    """Response for connection establishment"""
    success: bool
    message: str
    connection_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ConnectionStatus(BaseModel):
    """Connection status information"""
    source_type: DataSourceType
    connected: bool
    connection_id: Optional[str] = None
    last_connected: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


# ========== File/Content Models ==========
class FileInfo(BaseModel):
    """Generic file/document information"""
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="File/document name")
    type: str = Field(..., description="File type or content type")
    size: Optional[int] = Field(None, description="Size in bytes")
    modified_date: Optional[str] = Field(None, description="Last modified date")
    created_date: Optional[str] = Field(None, description="Creation date")
    path: Optional[str] = Field(None, description="File path or location")
    url: Optional[str] = Field(None, description="Web URL if available")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ListFilesRequest(BaseModel):
    """Request to list files from a data source"""
    source_type: Optional[DataSourceType] = None
    connection_id: str
    folder_path: Optional[str] = None
    space_key: Optional[str] = None  # For Confluence
    project_key: Optional[str] = None  # For JIRA
    file_types: Optional[List[str]] = None
    limit: int = Field(default=100, description="Maximum number of files to return")
    offset: int = Field(default=0, description="Offset for pagination")


class ListFilesResponse(BaseModel):
    """Response containing list of files"""
    success: bool
    files: List[FileInfo]
    total_count: int
    has_more: bool = False
    message: Optional[str] = None


# ========== Selection Models ==========
class FileSelectionRequest(BaseModel):
    """Request to select specific files for ingestion"""
    source_type: Optional[DataSourceType] = None
    connection_id: str
    file_ids: List[str] = Field(..., description="List of file IDs to select")


class FileSelectionResponse(BaseModel):
    """Response for file selection"""
    success: bool
    selected_count: int
    message: Optional[str] = None


# ========== Ingestion Models ==========
class IngestionRequest(BaseModel):
    """Request to ingest selected files into vector database"""
    source_type: Optional[DataSourceType] = None
    connection_id: str
    file_ids: List[str] = Field(..., description="List of file IDs to ingest")
    collection_name: Optional[str] = Field(None, description="Vector DB collection name")
    chunk_size: int = Field(default=1000, description="Text chunk size for embeddings")
    chunk_overlap: int = Field(default=200, description="Overlap between chunks")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata to attach")


class IngestionProgress(BaseModel):
    """Progress information for ingestion"""
    file_id: str
    file_name: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    chunks_created: Optional[int] = None
    error: Optional[str] = None


class IngestionResponse(BaseModel):
    """Response for ingestion request"""
    success: bool
    job_id: str
    message: str
    total_files: int
    progress: List[IngestionProgress] = []


class IngestionStatus(BaseModel):
    """Status of an ingestion job"""
    job_id: str
    status: str  # 'pending', 'in_progress', 'completed', 'failed'
    total_files: int
    completed_files: int
    failed_files: int
    progress: List[IngestionProgress]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


# ========== Search/Query Models ==========
class SearchRequest(BaseModel):
    """Search/filter request for data source"""
    source_type: Optional[DataSourceType] = None
    connection_id: str
    query: str = Field(..., description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Additional filters")
    limit: int = Field(default=50, description="Maximum results")


class SearchResponse(BaseModel):
    """Search results"""
    success: bool
    results: List[FileInfo]
    total_count: int
    message: Optional[str] = None


# ========== Confluence Specific Models ==========
class ConfluenceSpace(BaseModel):
    """Confluence space information"""
    key: str
    name: str
    type: str
    url: Optional[str] = None


class ConfluencePageInfo(FileInfo):
    """Extended file info for Confluence pages"""
    space_key: str
    parent_id: Optional[str] = None
    version: Optional[int] = None


# ========== JIRA Specific Models ==========
class JiraProject(BaseModel):
    """JIRA project information"""
    key: str
    name: str
    id: str
    project_type: Optional[str] = None


class JiraIssueInfo(FileInfo):
    """Extended file info for JIRA issues"""
    issue_key: str
    project_key: str
    issue_type: str
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None


# ========== Vector Store Models ==========
class VectorStoreConfig(BaseModel):
    """Vector store configuration"""
    store_type: str = Field(default="qdrant", description="Vector store type")
    collection_name: str = Field(..., description="Collection name")
    embedding_model: str = Field(default="text-embedding-3-small", description="OpenAI embedding model")
    qdrant_url: Optional[str] = Field(None, description="Qdrant server URL")
    qdrant_api_key: Optional[str] = Field(None, description="Qdrant API key")


class VectorStoreStats(BaseModel):
    """Vector store statistics"""
    collection_name: str
    total_vectors: int
    total_documents: int
    metadata: Optional[Dict[str, Any]] = None


# ========== Health Check Models ==========
class HealthCheck(BaseModel):
    """API health check response"""
    status: str
    version: str
    active_connections: int
    available_sources: List[DataSourceType]

"""
SharePoint Router - API endpoints for SharePoint operations
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List

try:
    from ..models import (
        ConnectionRequest,
        ConnectionResponse,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        DataSourceType,
        IngestionRequest,
        IngestionResponse
    )
    from ..config import get_connection_manager
    from ..services.sharepoint_service import SharePointService
    from ..services.vector_store_service import get_vector_store_service
    from ..utils.sharepoint_utils import SharePointUtils
except ImportError:
    from models import (
        ConnectionRequest,
        ConnectionResponse,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        DataSourceType,
        IngestionRequest,
        IngestionResponse
    )
    from config import get_connection_manager
    from services.sharepoint_service import SharePointService
    from services.vector_store_service import get_vector_store_service
    from utils.sharepoint_utils import SharePointUtils

router = APIRouter(prefix="/sharepoint", tags=["SharePoint"])


def get_sharepoint_client(connection_id: Optional[str] = None):
    """
    Get SharePoint client - either from connection manager or env variables
    Provides fallback mechanism for frontend flexibility
    """
    if connection_id:
        try:
            conn_manager = get_connection_manager()
            return conn_manager.get_client(connection_id)
        except Exception as e:
            raise HTTPException(400, f"Invalid connection_id: {str(e)}")
    else:
        # Fallback to environment variables
        try:
            return SharePointUtils()
        except Exception as e:
            raise HTTPException(
                500, 
                f"No connection_id provided and environment variables not configured: {str(e)}"
            )


@router.post("/connect", response_model=ConnectionResponse)
async def connect_sharepoint(request: ConnectionRequest):
    """
    Establish connection to SharePoint
    
    Required config fields:
    - site_url: SharePoint site URL
    - client_id: Azure AD client ID
    - client_secret: Azure AD client secret
    - tenant_id: Azure AD tenant ID
    """
    try:
        if request.source_type != DataSourceType.SHAREPOINT:
            raise HTTPException(400, "Invalid source type for SharePoint endpoint")
        
        conn_manager = get_connection_manager()
        connection_id, metadata = conn_manager.create_connection(
            DataSourceType.SHAREPOINT,
            request.config
        )
        
        return ConnectionResponse(
            success=True,
            message="Successfully connected to SharePoint",
            connection_id=connection_id,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to connect: {str(e)}")


@router.get("/test")
async def test_connection(connection_id: Optional[str] = None):
    """
    Test SharePoint connection
    Works with connection_id or environment variables
    """
    try:
        client = get_sharepoint_client(connection_id)
        return {
            "success": True,
            "message": "SharePoint connection successful",
            "site_url": getattr(client, 'site_url', 'N/A'),
            "using_env": connection_id is None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Connection test failed: {str(e)}")


@router.get("/sites")
async def list_sites(connection_id: Optional[str] = None):
    """
    List accessible SharePoint sites
    Works with connection_id or environment variables
    """
    try:
        client = get_sharepoint_client(connection_id)
        service = SharePointService(client)
        sites = service.list_sites()
        
        return {
            "success": True,
            "sites": sites,
            "count": len(sites)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to list sites: {str(e)}")


@router.get("/libraries")
async def list_libraries(
    connection_id: Optional[str] = None,
    site_id: Optional[str] = None
):
    """
    List document libraries
    Works with connection_id or environment variables
    """
    try:
        client = get_sharepoint_client(connection_id)
        service = SharePointService(client)
        libraries = service.list_libraries(site_id)
        
        return {
            "success": True,
            "libraries": libraries,
            "count": len(libraries)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to list libraries: {str(e)}")


@router.get("/files")
async def list_files_get(
    connection_id: Optional[str] = None,
    library_name: str = "Documents",
    folder_path: str = "",
    file_types: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """
    List files from SharePoint (GET endpoint)
    
    Query parameters:
    - connection_id: Optional connection ID (uses env if not provided)
    - library_name: Document library name (default: Documents)
    - folder_path: Folder path within library
    - file_types: Comma-separated file extensions (e.g., "pdf,docx")
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        client = get_sharepoint_client(connection_id)
        service = SharePointService(client)
        
        # Parse file_types if provided
        file_types_list = None
        if file_types:
            file_types_list = [ft.strip() for ft in file_types.split(",")]
        
        result = service.list_files(
            library_name=library_name,
            folder_path=folder_path if folder_path else None,
            file_types=file_types_list,
            limit=limit,
            offset=offset
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to list files: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_files(request: ListFilesRequest):
    """
    List files from SharePoint (POST endpoint for complex requests)
    
    Optional parameters:
    - connection_id: Optional connection ID (uses env if not provided)
    - folder_path: Library name or folder path
    - file_types: List of file extensions to filter
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        client = get_sharepoint_client(request.connection_id)
        service = SharePointService(client)
        
        return service.list_files(
            library_name=request.folder_path,
            file_types=request.file_types,
            limit=request.limit,
            offset=request.offset
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to list files: {str(e)}")


@router.get("/search")
async def search_files_get(
    query: str,
    connection_id: Optional[str] = None,
    library_name: Optional[str] = None,
    file_types: Optional[str] = None,
    limit: int = 50
):
    """
    Search files in SharePoint (GET endpoint)
    
    Query parameters:
    - query: Search query string (required)
    - connection_id: Optional connection ID (uses env if not provided)
    - library_name: Limit search to specific library
    - file_types: Comma-separated file extensions
    - limit: Maximum number of results
    """
    try:
        client = get_sharepoint_client(connection_id)
        service = SharePointService(client)
        
        # Parse file_types if provided
        file_types_list = None
        if file_types:
            file_types_list = [ft.strip() for ft in file_types.split(",")]
        
        result = service.search_files(
            query=query,
            library_name=library_name,
            file_types=file_types_list,
            limit=limit
        )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    Search files in SharePoint (POST endpoint for complex requests)
    
    Filters supported in request.filters:
    - library_name: Search within a specific library
    - file_types: Filter by file extensions
    """
    try:
        client = get_sharepoint_client(request.connection_id)
        service = SharePointService(client)
        filters = request.filters or {}
        
        return service.search_files(
            query=request.query,
            library_name=filters.get('library_name'),
            file_types=filters.get('file_types'),
            limit=request.limit
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.get("/files/{file_id}/metadata")
async def get_file_metadata(
    file_id: str,
    connection_id: Optional[str] = None
):
    """
    Get detailed metadata for a specific file
    Works with connection_id or environment variables
    """
    try:
        client = get_sharepoint_client(connection_id)
        service = SharePointService(client)
        metadata = service.get_file_metadata(file_id)
        
        return {
            "success": True,
            "metadata": metadata
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to get file metadata: {str(e)}")


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_files(request: IngestionRequest):
    """
    Ingest selected SharePoint files into vector database
    Works with connection_id or environment variables
    """
    try:
        # Set source type for this endpoint
        request.source_type = DataSourceType.SHAREPOINT
        
        # Get client (with fallback to env)
        client = get_sharepoint_client(request.connection_id)
        
        # Create ingestion job
        vector_service = get_vector_store_service()
        response = vector_service.create_ingestion_job(request)
        
        # Process ingestion immediately
        vector_service.process_ingestion(
            response.job_id,
            client,
            DataSourceType.SHAREPOINT
        )
        
        # Get updated status
        status = vector_service.get_job_status(response.job_id)
        response.progress = status.progress
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Failed to ingest files: {str(e)}")

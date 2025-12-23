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

router = APIRouter(prefix="/sharepoint", tags=["SharePoint"])


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


@router.get("/sites")
async def list_sites(connection_id: str):
    """List accessible SharePoint sites"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = SharePointService(client)
        sites = service.list_sites()
        
        return {
            "success": True,
            "sites": sites,
            "count": len(sites)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list sites: {str(e)}")


@router.get("/libraries")
async def list_libraries(
    connection_id: str,
    site_id: Optional[str] = None
):
    """List document libraries"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = SharePointService(client)
        libraries = service.list_libraries(site_id)
        
        return {
            "success": True,
            "libraries": libraries,
            "count": len(libraries)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list libraries: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_files(request: ListFilesRequest):
    """
    List files from SharePoint
    
    Optional parameters:
    - folder_path: Library name or folder path
    - file_types: List of file extensions to filter
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = SharePointService(client)
        return service.list_files(
            library_name=request.folder_path,
            file_types=request.file_types,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list files: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    Search files in SharePoint
    
    Filters supported in request.filters:
    - library_name: Search within a specific library
    - file_types: Filter by file extensions
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = SharePointService(client)
        filters = request.filters or {}
        
        return service.search_files(
            query=request.query,
            library_name=filters.get('library_name'),
            file_types=filters.get('file_types'),
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.get("/files/{file_id}/metadata")
async def get_file_metadata(
    connection_id: str,
    file_id: str
):
    """Get detailed metadata for a specific file"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = SharePointService(client)
        metadata = service.get_file_metadata(file_id)
        
        return {
            "success": True,
            "metadata": metadata
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get file metadata: {str(e)}")


@router.post("/ingest", response_model=IngestionResponse)
async def ingest_files(request: IngestionRequest):
    """
    Ingest selected SharePoint files into vector database
    """
    try:
        # Set source type for this endpoint
        request.source_type = DataSourceType.SHAREPOINT
        
        # Validate connection
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
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
    
    except Exception as e:
        raise HTTPException(500, f"Failed to ingest files: {str(e)}")

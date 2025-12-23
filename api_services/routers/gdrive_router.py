"""
Google Drive Router - API endpoints for Google Drive operations
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
    from ..services.gdrive_service import GDriveService
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
    from services.gdrive_service import GDriveService
    from services.vector_store_service import get_vector_store_service

router = APIRouter(prefix="/gdrive", tags=["Google Drive"])


@router.post("/connect", response_model=ConnectionResponse)
async def connect_gdrive(request: ConnectionRequest):
    """
    Establish connection to Google Drive
    
    Required config fields:
    - service_account_json: Service account JSON content or file path
    - credentials_type: Either 'json_string' or 'file_path'
    """
    try:
        if request.source_type != DataSourceType.GDRIVE:
            raise HTTPException(400, "Invalid source type for Google Drive endpoint")
        
        conn_manager = get_connection_manager()
        connection_id, metadata = conn_manager.create_connection(
            DataSourceType.GDRIVE,
            request.config
        )
        
        return ConnectionResponse(
            success=True,
            message="Successfully connected to Google Drive",
            connection_id=connection_id,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to connect: {str(e)}")


@router.get("/folders")
async def list_folders(
    connection_id: str,
    parent_folder_name: str = "root"
):
    """List folders in Google Drive or within a specific folder"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = GDriveService(client)
        folders = service.list_folders(parent_folder_name)
        
        return {
            "success": True,
            "folders": folders,
            "count": len(folders)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list folders: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_files(request: ListFilesRequest):
    """
    List files from Google Drive
    
    Optional parameters:
    - folder_path: Folder name or "root"
    - file_types: List of file extensions to filter
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = GDriveService(client)
        return service.list_files(
            folder_name=request.folder_path or "root",
            file_types=request.file_types,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list files: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    Search files in Google Drive
    
    Filters supported in request.filters:
    - folder_name: Search within a specific folder
    - file_types: Filter by file extensions
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = GDriveService(client)
        filters = request.filters or {}
        
        return service.search_files(
            query=request.query,
            file_types=filters.get('file_types'),
            folder_name=filters.get('folder_name'),
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
        
        service = GDriveService(client)
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
    Ingest selected Google Drive files into vector database
    """
    try:
        # Set source type for this endpoint
        request.source_type = DataSourceType.GDRIVE
        
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
            DataSourceType.GDRIVE
        )
        
        # Get updated status
        status = vector_service.get_job_status(response.job_id)
        response.progress = status.progress
        
        return response
    
    except Exception as e:
        raise HTTPException(500, f"Failed to ingest files: {str(e)}")

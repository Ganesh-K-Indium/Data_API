"""
Local PDF Router - API endpoints for local PDF operations
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

try:
    from ..models import (
        ConnectionRequest,
        ConnectionResponse,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        DataSourceType
    )
    from ..config import get_connection_manager
    from ..services.local_pdf_service import LocalPDFService
except ImportError:
    from models import (
        ConnectionRequest,
        ConnectionResponse,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        DataSourceType
    )
    from config import get_connection_manager
    from services.local_pdf_service import LocalPDFService

router = APIRouter(prefix="/local-pdf", tags=["Local PDF"])


@router.post("/connect", response_model=ConnectionResponse)
async def connect_local_pdf(request: ConnectionRequest):
    """
    Connect to local PDF directory
    
    Required config fields:
    - base_directory: Base directory path for PDF files
    """
    try:
        if request.source_type != DataSourceType.LOCAL_PDF:
            raise HTTPException(400, "Invalid source type for Local PDF endpoint")
        
        conn_manager = get_connection_manager()
        connection_id, metadata = conn_manager.create_connection(
            DataSourceType.LOCAL_PDF,
            request.config
        )
        
        return ConnectionResponse(
            success=True,
            message="Successfully connected to local PDF directory",
            connection_id=connection_id,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to connect: {str(e)}")


@router.get("/directories")
async def list_directories(
    connection_id: str,
    parent_path: Optional[str] = None
):
    """List subdirectories in the PDF directory"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = LocalPDFService(client)
        directories = service.list_directories(parent_path)
        
        return {
            "success": True,
            "directories": directories,
            "count": len(directories)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list directories: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_files(request: ListFilesRequest):
    """
    List PDF files from local directory
    
    Optional parameters:
    - folder_path: Subfolder path
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = LocalPDFService(client)
        return service.list_files(
            folder_path=request.folder_path,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list files: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    Search PDF files by name
    
    Filters supported in request.filters:
    - folder_path: Search within a specific folder
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = LocalPDFService(client)
        filters = request.filters or {}
        
        return service.search_files(
            query=request.query,
            folder_path=filters.get('folder_path'),
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")

"""
Confluence Router - API endpoints for Confluence operations
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List

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
    from ..services.confluence_service import ConfluenceService
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
    from services.confluence_service import ConfluenceService

router = APIRouter(prefix="/confluence", tags=["Confluence"])


@router.post("/connect", response_model=ConnectionResponse)
async def connect_confluence(request: ConnectionRequest):
    """
    Establish connection to Confluence instance
    
    Required config fields:
    - url: Confluence instance URL
    - username: Confluence username/email
    - api_token: Confluence API token
    - cloud: Boolean (default: True)
    """
    try:
        if request.source_type != DataSourceType.CONFLUENCE:
            raise HTTPException(400, "Invalid source type for Confluence endpoint")
        
        conn_manager = get_connection_manager()
        connection_id, metadata = conn_manager.create_connection(
            DataSourceType.CONFLUENCE,
            request.config
        )
        
        return ConnectionResponse(
            success=True,
            message="Successfully connected to Confluence",
            connection_id=connection_id,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to connect: {str(e)}")


@router.get("/spaces")
async def list_spaces(
    connection_id: str,
    limit: int = 50
):
    """List all accessible Confluence spaces"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = ConfluenceService(client)
        spaces = service.list_spaces(limit=limit)
        
        return {
            "success": True,
            "spaces": [space.dict() for space in spaces],
            "count": len(spaces)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list spaces: {str(e)}")


@router.get("/spaces/{space_key}")
async def get_space_info(
    connection_id: str,
    space_key: str
):
    """Get detailed information about a specific space"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = ConfluenceService(client)
        space_info = service.get_space_info(space_key)
        
        return {
            "success": True,
            "space": space_info
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get space info: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_pages(request: ListFilesRequest):
    """
    List pages from Confluence
    
    Optional filters:
    - space_key: Filter by space
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = ConfluenceService(client)
        return service.list_pages(
            space_key=request.space_key,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list pages: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_content(request: SearchRequest):
    """
    Search Confluence content
    
    Filters supported in request.filters:
    - space_key: Search within a specific space
    - content_type: Filter by type (page, blogpost, etc.)
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = ConfluenceService(client)
        filters = request.filters or {}
        
        return service.search_content(
            query=request.query,
            space_key=filters.get('space_key'),
            content_type=filters.get('content_type'),
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.get("/pages/{page_id}")
async def get_page_content(
    connection_id: str,
    page_id: str
):
    """Get full content of a specific page"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = ConfluenceService(client)
        content = service.get_page_content(page_id)
        
        return {
            "success": True,
            "page": content
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get page content: {str(e)}")


@router.get("/pages/{page_id}/children")
async def get_page_children(
    connection_id: str,
    page_id: str,
    limit: int = 50
):
    """Get child pages of a specific page"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = ConfluenceService(client)
        children = service.get_page_children(page_id, limit)
        
        return {
            "success": True,
            "children": [child.dict() for child in children],
            "count": len(children)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get child pages: {str(e)}")

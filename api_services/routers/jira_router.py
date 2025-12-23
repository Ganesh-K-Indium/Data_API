"""
JIRA Router - API endpoints for JIRA operations
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
    from ..services.jira_service import JiraService
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
    from services.jira_service import JiraService

router = APIRouter(prefix="/jira", tags=["JIRA"])


@router.post("/connect", response_model=ConnectionResponse)
async def connect_jira(request: ConnectionRequest):
    """
    Establish connection to JIRA instance
    
    Required config fields:
    - url: JIRA instance URL
    - username: JIRA username/email
    - api_token: JIRA API token
    - cloud: Boolean (default: True)
    """
    try:
        if request.source_type != DataSourceType.JIRA:
            raise HTTPException(400, "Invalid source type for JIRA endpoint")
        
        conn_manager = get_connection_manager()
        connection_id, metadata = conn_manager.create_connection(
            DataSourceType.JIRA,
            request.config
        )
        
        return ConnectionResponse(
            success=True,
            message="Successfully connected to JIRA",
            connection_id=connection_id,
            metadata=metadata
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to connect: {str(e)}")


@router.get("/projects")
async def list_projects(connection_id: str):
    """List all accessible JIRA projects"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = JiraService(client)
        projects = service.list_projects()
        
        return {
            "success": True,
            "projects": [p.dict() for p in projects],
            "count": len(projects)
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list projects: {str(e)}")


@router.post("/list-files", response_model=ListFilesResponse)
async def list_issues(request: ListFilesRequest):
    """
    List issues from JIRA
    
    Optional parameters:
    - project_key: Filter by project
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = JiraService(client)
        return service.list_issues(
            project_key=request.project_key,
            limit=request.limit,
            offset=request.offset
        )
    
    except Exception as e:
        raise HTTPException(500, f"Failed to list issues: {str(e)}")


@router.post("/search", response_model=SearchResponse)
async def search_issues(request: SearchRequest):
    """
    Search JIRA issues
    
    Filters supported in request.filters:
    - project_key: Search within a specific project
    """
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        service = JiraService(client)
        filters = request.filters or {}
        
        return service.search_issues(
            query=request.query,
            project_key=filters.get('project_key'),
            limit=request.limit
        )
    
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@router.get("/issues/{issue_key}")
async def get_issue_details(
    connection_id: str,
    issue_key: str
):
    """Get detailed information about a specific issue"""
    try:
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(connection_id)
        
        service = JiraService(client)
        details = service.get_issue_details(issue_key)
        
        return {
            "success": True,
            "issue": details
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get issue details: {str(e)}")

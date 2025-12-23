"""
Confluence Service - Business logic for Confluence operations
"""
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from ..models import (
        FileInfo,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        ConfluenceSpace
    )
except ImportError:
    from models import (
        FileInfo,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse,
        ConfluenceSpace
    )


class ConfluenceService:
    """Service layer for Confluence operations"""
    
    def __init__(self, client):
        """
        Initialize with a Confluence client
        
        Args:
            client: ConfluenceUtils instance
        """
        self.client = client
        self.confluence = client.confluence_client
    
    def list_spaces(self, limit: int = 50) -> List[ConfluenceSpace]:
        """List all accessible Confluence spaces"""
        try:
            spaces_result = self.confluence.get_spaces(limit=limit)
            spaces = []
            
            for space in spaces_result.get('results', []):
                spaces.append(ConfluenceSpace(
                    key=space.get('key', ''),
                    name=space.get('name', ''),
                    type=space.get('type', ''),
                    url=space.get('_links', {}).get('webui', '')
                ))
            
            return spaces
        except Exception as e:
            raise Exception(f"Failed to list spaces: {str(e)}")
    
    def get_space_info(self, space_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific space"""
        try:
            space = self.confluence.get_space(space_key, expand=['description', 'homepage'])
            return {
                'key': space.get('key', ''),
                'name': space.get('name', ''),
                'type': space.get('type', ''),
                'description': space.get('description', {}).get('plain', {}).get('value', ''),
                'homepage_id': space.get('homepage', {}).get('id', ''),
                'url': space.get('_links', {}).get('webui', '')
            }
        except Exception as e:
            raise Exception(f"Failed to get space info: {str(e)}")
    
    def list_pages(
        self,
        space_key: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> ListFilesResponse:
        """List pages from Confluence"""
        try:
            # Build CQL query
            cql_parts = ["type=page"]
            if space_key:
                cql_parts.append(f"space={space_key}")
            
            cql = " AND ".join(cql_parts)
            
            # Search for pages
            results = self.confluence.search_content(
                cql=cql,
                limit=limit,
                start=offset,
                expand='space,version,history.lastUpdated'
            )
            
            files = []
            for page in results.get('results', []):
                page_id = str(page.get('id', ''))
                page_title = page.get('title', 'Untitled')
                space_key = page.get('space', {}).get('key', '')
                
                # Try to get page size from body content if available
                page_size = None
                if page.get('body', {}).get('storage', {}).get('value'):
                    page_size = len(page.get('body', {}).get('storage', {}).get('value', ''))
                
                files.append(FileInfo(
                    id=page_id,
                    name=page_title,
                    type='page',
                    size=page_size,
                    path=f"{space_key}/{page_title}",
                    url=page.get('_links', {}).get('webui', ''),
                    created_date=page.get('history', {}).get('createdDate', ''),
                    modified_date=page.get('version', {}).get('when', ''),
                    metadata={
                        'space_key': space_key,
                        'space_name': page.get('space', {}).get('name', ''),
                        'version': page.get('version', {}).get('number', 1),
                        'status': page.get('status', 'current'),
                        'content_type': 'confluence_page'
                    }
                ))
            
            total = results.get('totalSize', len(files))
            has_more = (offset + len(files)) < total
            
            return ListFilesResponse(
                success=True,
                files=files,
                total_count=total,
                has_more=has_more
            )
        
        except Exception as e:
            return ListFilesResponse(
                success=False,
                files=[],
                total_count=0,
                message=f"Failed to list pages: {str(e)}"
            )
    
    def search_content(
        self,
        query: str,
        space_key: Optional[str] = None,
        content_type: Optional[str] = None,
        limit: int = 50
    ) -> SearchResponse:
        """Search Confluence content"""
        try:
            # Build CQL query
            cql_parts = []
            
            if query:
                cql_parts.append(f'text ~ "{query}"')
            
            if space_key:
                cql_parts.append(f"space={space_key}")
            
            if content_type:
                cql_parts.append(f"type={content_type}")
            else:
                cql_parts.append("type=page")  # Default to pages
            
            cql = " AND ".join(cql_parts)
            
            # Execute search
            results = self.confluence.search_content(
                cql=cql,
                limit=limit,
                expand='space,version'
            )
            
            files = []
            for item in results.get('results', []):
                files.append(FileInfo(
                    id=item.get('id', ''),
                    name=item.get('title', ''),
                    type=item.get('type', 'page'),
                    url=item.get('_links', {}).get('webui', ''),
                    metadata={
                        'space_key': item.get('space', {}).get('key', ''),
                        'version': item.get('version', {}).get('number', 1)
                    }
                ))
            
            return SearchResponse(
                success=True,
                results=files,
                total_count=results.get('totalSize', len(files))
            )
        
        except Exception as e:
            return SearchResponse(
                success=False,
                results=[],
                total_count=0,
                message=f"Search failed: {str(e)}"
            )
    
    def get_page_content(self, page_id: str) -> Dict[str, Any]:
        """Get full content of a specific page"""
        try:
            page = self.confluence.get_page_by_id(
                page_id,
                expand='body.storage,body.view,space,version,history'
            )
            
            return {
                'id': page.get('id', ''),
                'title': page.get('title', ''),
                'space_key': page.get('space', {}).get('key', ''),
                'content_html': page.get('body', {}).get('storage', {}).get('value', ''),
                'content_view': page.get('body', {}).get('view', {}).get('value', ''),
                'version': page.get('version', {}).get('number', 1),
                'created_date': page.get('history', {}).get('createdDate', ''),
                'modified_date': page.get('version', {}).get('when', ''),
                'url': page.get('_links', {}).get('webui', '')
            }
        except Exception as e:
            raise Exception(f"Failed to get page content: {str(e)}")
    
    def get_page_children(self, page_id: str, limit: int = 50) -> List[FileInfo]:
        """Get child pages of a specific page"""
        try:
            children = self.confluence.get_page_child_by_type(
                page_id,
                type='page',
                limit=limit,
                expand='space,version'
            )
            
            files = []
            for child in children.get('results', []):
                files.append(FileInfo(
                    id=child.get('id', ''),
                    name=child.get('title', ''),
                    type='page',
                    url=child.get('_links', {}).get('webui', ''),
                    metadata={
                        'parent_id': page_id,
                        'space_key': child.get('space', {}).get('key', ''),
                        'version': child.get('version', {}).get('number', 1)
                    }
                ))
            
            return files
        except Exception as e:
            raise Exception(f"Failed to get child pages: {str(e)}")

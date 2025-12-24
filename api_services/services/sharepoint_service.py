"""
SharePoint Service - Business logic for SharePoint operations
"""
import os
from typing import List, Dict, Any, Optional

try:
    from ..models import (
        FileInfo,
        ListFilesResponse,
        SearchResponse
    )
except ImportError:
    from models import (
        FileInfo,
        ListFilesResponse,
        SearchResponse
    )


class SharePointService:
    """Service layer for SharePoint operations"""
    
    def __init__(self, client):
        self.client = client
    
    def list_sites(self) -> List[Dict[str, Any]]:
        """List accessible SharePoint sites"""
        try:
            sites = self.client.list_sites()
            return sites
        except Exception as e:
            raise Exception(f"Failed to list sites: {str(e)}")
    
    def list_libraries(self, site_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List document libraries"""
        try:
            libraries = self.client.list_document_libraries(site_id)
            return libraries
        except Exception as e:
            raise Exception(f"Failed to list libraries: {str(e)}")
    
    def list_files(
        self,
        library_name: Optional[str] = None,
        folder_path: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> ListFilesResponse:
        """List files from SharePoint"""
        try:
            files_data = self.client.list_files(
                library_name=library_name,
                folder_path=folder_path,
                file_types=file_types
            )
            
            # Convert to FileInfo objects
            files = []
            for file_data in files_data[offset:offset + limit]:
                files.append(FileInfo(
                    id=file_data.get('id', ''),
                    name=file_data.get('name', ''),
                    type=file_data.get('type', ''),
                    size=file_data.get('size'),
                    modified_date=file_data.get('modified_date', ''),
                    created_date=file_data.get('created_date', ''),
                    path=file_data.get('path', ''),
                    url=file_data.get('url', ''),
                    metadata={
                        'library': library_name,
                        'server_relative_url': file_data.get('server_relative_url', ''),
                        'downloadUrl': file_data.get('downloadUrl', '')
                    }
                ))
            
            return ListFilesResponse(
                success=True,
                files=files,
                total_count=len(files_data),
                has_more=(offset + len(files)) < len(files_data)
            )
        
        except Exception as e:
            return ListFilesResponse(
                success=False,
                files=[],
                total_count=0,
                message=f"Failed to list files: {str(e)}"
            )
    
    def search_files(
        self,
        query: str,
        library_name: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        limit: int = 50
    ) -> SearchResponse:
        """Search files in SharePoint"""
        try:
            results = self.client.search_files(
                query=query,
                library_name=library_name,
                file_types=file_types,
                max_results=limit
            )
            
            files = []
            for file_data in results:
                files.append(FileInfo(
                    id=file_data.get('id', ''),
                    name=file_data.get('name', ''),
                    type=file_data.get('type', ''),
                    size=file_data.get('size'),
                    url=file_data.get('url', ''),
                    metadata={
                        'library': library_name,
                        'path': file_data.get('path', '')
                    }
                ))
            
            return SearchResponse(
                success=True,
                results=files,
                total_count=len(files)
            )
        
        except Exception as e:
            return SearchResponse(
                success=False,
                results=[],
                total_count=0,
                message=f"Search failed: {str(e)}"
            )
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get detailed metadata for a specific file"""
        try:
            metadata = self.client.get_file_properties(file_id)
            return metadata
        except Exception as e:
            raise Exception(f"Failed to get file metadata: {str(e)}")

"""
Google Drive Service - Business logic for Google Drive operations
"""
from typing import List, Dict, Any, Optional
import os

try:
    from ..models import (
        FileInfo,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse
    )
except ImportError:
    from models import (
        FileInfo,
        ListFilesRequest,
        ListFilesResponse,
        SearchRequest,
        SearchResponse
    )


class GDriveService:
    """Service layer for Google Drive operations"""
    
    def __init__(self, client):
        """
        Initialize with a Google Drive client
        
        Args:
            client: GoogleDriveClient instance
        """
        self.client = client
    
    def list_folders(self, parent_folder_name: str = "root") -> List[Dict[str, Any]]:
        """List folders in Google Drive"""
        try:
            parent_id = "root"
            if parent_folder_name != "root":
                parent_id = self.client.find_folder_by_name(parent_folder_name)
                if not parent_id:
                    raise ValueError(f"Folder not found: {parent_folder_name}")
            
            folders = self.client.list_folders(parent_id=parent_id)
            return folders
        
        except Exception as e:
            raise Exception(f"Failed to list folders: {str(e)}")
    
    def list_files(
        self,
        folder_name: str = "root",
        file_types: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> ListFilesResponse:
        """List files from Google Drive"""
        try:
            # Find folder ID
            folder_id = "root"
            if folder_name != "root":
                folder_id = self.client.find_folder_by_name(folder_name)
                if not folder_id:
                    return ListFilesResponse(
                        success=False,
                        files=[],
                        total_count=0,
                        message=f"Folder not found: {folder_name}"
                    )
            
            # List files
            files_data = self.client.list_files(
                folder_id=folder_id,
                file_types=file_types,
                max_results=limit
            )
            
            # Convert to FileInfo objects
            files = []
            for file_data in files_data:
                files.append(FileInfo(
                    id=file_data.get('id', ''),
                    name=file_data.get('name', ''),
                    type=file_data.get('mimeType', ''),
                    size=int(file_data.get('size', 0)) if file_data.get('size') else None,
                    modified_date=file_data.get('modifiedTime', ''),
                    created_date=file_data.get('createdTime', ''),
                    path=f"{folder_name}/{file_data.get('name', '')}",
                    url=file_data.get('webViewLink', ''),
                    metadata={
                        'folder_id': folder_id,
                        'mime_type': file_data.get('mimeType', ''),
                        'owners': file_data.get('owners', [])
                    }
                ))
            
            # Apply offset
            files = files[offset:offset + limit]
            
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
        file_types: Optional[List[str]] = None,
        folder_name: Optional[str] = None,
        limit: int = 50
    ) -> SearchResponse:
        """Search files in Google Drive"""
        try:
            # Build search query
            query_parts = [f"name contains '{query}'"]
            
            if file_types:
                mime_types = [self._get_mime_type(ft) for ft in file_types]
                mime_query = " or ".join([f"mimeType='{mt}'" for mt in mime_types if mt])
                if mime_query:
                    query_parts.append(f"({mime_query})")
            
            if folder_name and folder_name != "root":
                folder_id = self.client.find_folder_by_name(folder_name)
                if folder_id:
                    query_parts.append(f"'{folder_id}' in parents")
            
            search_query = " and ".join(query_parts)
            
            # Execute search
            results = self.client.service.files().list(
                q=search_query,
                pageSize=limit,
                fields="files(id, name, mimeType, size, modifiedTime, createdTime, webViewLink, owners)"
            ).execute()
            
            files = []
            for file_data in results.get('files', []):
                files.append(FileInfo(
                    id=file_data.get('id', ''),
                    name=file_data.get('name', ''),
                    type=file_data.get('mimeType', ''),
                    size=int(file_data.get('size', 0)) if file_data.get('size') else None,
                    modified_date=file_data.get('modifiedTime', ''),
                    created_date=file_data.get('createdTime', ''),
                    url=file_data.get('webViewLink', ''),
                    metadata={
                        'mime_type': file_data.get('mimeType', ''),
                        'owners': file_data.get('owners', [])
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
            file_data = self.client.service.files().get(
                fileId=file_id,
                fields="*"
            ).execute()
            
            return {
                'id': file_data.get('id', ''),
                'name': file_data.get('name', ''),
                'mime_type': file_data.get('mimeType', ''),
                'size': file_data.get('size', 0),
                'created_time': file_data.get('createdTime', ''),
                'modified_time': file_data.get('modifiedTime', ''),
                'web_view_link': file_data.get('webViewLink', ''),
                'owners': file_data.get('owners', []),
                'parents': file_data.get('parents', []),
                'permissions': file_data.get('permissions', [])
            }
        
        except Exception as e:
            raise Exception(f"Failed to get file metadata: {str(e)}")
    
    def _get_mime_type(self, file_extension: str) -> Optional[str]:
        """Convert file extension to MIME type"""
        mime_types = {
            'pdf': 'application/pdf',
            'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'csv': 'text/csv',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png'
        }
        return mime_types.get(file_extension.lower())

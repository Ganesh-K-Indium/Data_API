"""
Local PDF Service - Business logic for local PDF operations
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

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


class LocalPDFService:
    """Service layer for local PDF operations"""
    
    def __init__(self, client):
        self.client = client
        self.base_directory = client.base_directory
    
    def list_files(
        self,
        folder_path: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> ListFilesResponse:
        """List PDF files from local directory"""
        try:
            target_dir = self.base_directory
            if folder_path:
                target_dir = os.path.join(self.base_directory, folder_path)
            
            if not os.path.exists(target_dir):
                return ListFilesResponse(
                    success=False,
                    files=[],
                    total_count=0,
                    message=f"Directory not found: {target_dir}"
                )
            
            # Find all PDF files
            pdf_files = []
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        file_path = os.path.join(root, file)
                        pdf_files.append(file_path)
            
            # Create FileInfo objects
            files = []
            for file_path in pdf_files[offset:offset + limit]:
                rel_path = os.path.relpath(file_path, self.base_directory)
                stat = os.stat(file_path)
                
                files.append(FileInfo(
                    id=file_path,
                    name=os.path.basename(file_path),
                    type='application/pdf',
                    size=stat.st_size,
                    modified_date=str(stat.st_mtime),
                    path=rel_path,
                    metadata={
                        'full_path': file_path,
                        'directory': os.path.dirname(rel_path)
                    }
                ))
            
            return ListFilesResponse(
                success=True,
                files=files,
                total_count=len(pdf_files),
                has_more=(offset + len(files)) < len(pdf_files)
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
        folder_path: Optional[str] = None,
        limit: int = 50
    ) -> SearchResponse:
        """Search PDF files by name"""
        try:
            target_dir = self.base_directory
            if folder_path:
                target_dir = os.path.join(self.base_directory, folder_path)
            
            # Find matching PDF files
            matching_files = []
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.lower().endswith('.pdf') and query.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        matching_files.append(file_path)
                        
                        if len(matching_files) >= limit:
                            break
                if len(matching_files) >= limit:
                    break
            
            # Create FileInfo objects
            files = []
            for file_path in matching_files:
                rel_path = os.path.relpath(file_path, self.base_directory)
                stat = os.stat(file_path)
                
                files.append(FileInfo(
                    id=file_path,
                    name=os.path.basename(file_path),
                    type='application/pdf',
                    size=stat.st_size,
                    modified_date=str(stat.st_mtime),
                    path=rel_path,
                    metadata={
                        'full_path': file_path,
                        'directory': os.path.dirname(rel_path)
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
    
    def list_directories(self, parent_path: Optional[str] = None) -> List[Dict[str, str]]:
        """List subdirectories"""
        try:
            target_dir = self.base_directory
            if parent_path:
                target_dir = os.path.join(self.base_directory, parent_path)
            
            directories = []
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isdir(item_path):
                    rel_path = os.path.relpath(item_path, self.base_directory)
                    directories.append({
                        'name': item,
                        'path': rel_path,
                        'full_path': item_path
                    })
            
            return directories
        
        except Exception as e:
            raise Exception(f"Failed to list directories: {str(e)}")

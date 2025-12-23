"""
Vector Store Service for document ingestion
Handles embedding and storage of documents from various sources
Uses the existing proven ingestion pipeline from pdf_processor1.py and image_data_prep.py
"""
import os
import sys
import json
import uuid
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Import existing proven utilities
try:
    from ..vector_store.load_dbs import load_vector_database
    from ..utility.pdf_processor1 import process_pdf_and_stream
    from ..data_preparation.image_data_prep import ImageDescription
    from ..models import (
        IngestionRequest,
        IngestionResponse,
        IngestionProgress,
        IngestionStatus,
        DataSourceType
    )
except ImportError:
    from vector_store.load_dbs import load_vector_database
    from utility.pdf_processor1 import process_pdf_and_stream
    from data_preparation.image_data_prep import ImageDescription
    from models import (
        IngestionRequest,
        IngestionResponse,
        IngestionProgress,
        IngestionStatus,
        DataSourceType
    )


class VectorStoreService:
    """Service for managing vector store operations using existing proven pipeline"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Initialize vector stores using existing load_dbs utility
        self.db_loader = load_vector_database()
        
        # Track ingestion jobs
        self.ingestion_jobs: Dict[str, Dict[str, Any]] = {}
    
    def _get_vector_stores(self):
        """Get text and image vector stores using existing utility"""
        try:
            text_retriever, text_vectorstore, _ = self.db_loader.get_text_retriever()
            image_vectorstore, image_retriever, _ = self.db_loader.get_image_retriever()
            return text_vectorstore, image_vectorstore
        except Exception as e:
            print(f"Error getting vector stores: {e}")
            raise
    
    def create_ingestion_job(
        self,
        request: IngestionRequest
    ) -> IngestionResponse:
        """Create a new ingestion job"""
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        # Initialize job tracking
        self.ingestion_jobs[job_id] = {
            'job_id': job_id,
            'status': 'pending',
            'source_type': request.source_type,
            'connection_id': request.connection_id,
            'file_ids': request.file_ids,
            'collection_name': request.collection_name or f"collection_{request.source_type.value}",
            'total_files': len(request.file_ids),
            'completed_files': 0,
            'failed_files': 0,
            'progress': [],
            'started_at': datetime.now().isoformat(),
            'chunk_size': request.chunk_size,
            'chunk_overlap': request.chunk_overlap,
            'metadata': request.metadata or {}
        }
        
        return IngestionResponse(
            success=True,
            job_id=job_id,
            message=f"Ingestion job created for {len(request.file_ids)} files",
            total_files=len(request.file_ids),
            progress=[]
        )
    
    def get_job_status(self, job_id: str) -> IngestionStatus:
        """Get the status of an ingestion job"""
        if job_id not in self.ingestion_jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self.ingestion_jobs[job_id]
        return IngestionStatus(**job)
    
    def process_ingestion(
        self,
        job_id: str,
        client,
        source_type: DataSourceType
    ):
        """Process the ingestion job using existing proven pipeline"""
        if job_id not in self.ingestion_jobs:
            raise ValueError(f"Job not found: {job_id}")
        
        job = self.ingestion_jobs[job_id]
        job['status'] = 'in_progress'
        
        file_ids = job['file_ids']
        base_metadata = job['metadata']
        
        # Process each file
        for file_id in file_ids:
            progress_item = IngestionProgress(
                file_id=file_id,
                file_name=file_id,
                status='processing',
                chunks_created=0
            )
            
            try:
                # Download/fetch file to temporary location
                temp_file_path = self._fetch_and_save_file(
                    client,
                    source_type,
                    file_id
                )
                
                if temp_file_path:
                    # Use existing proven PDF processing pipeline
                    messages = []
                    for message in process_pdf_and_stream(temp_file_path):
                        messages.append(message)
                        print(f"[{source_type.value}] {message}")
                    
                    # Parse results from messages
                    chunks_created = 0
                    for msg in messages:
                        if "Added" in msg and "chunks" in msg:
                            import re
                            match = re.search(r'Added (\d+)', msg)
                            if match:
                                chunks_created += int(match.group(1))
                    
                    progress_item.status = 'completed'
                    progress_item.chunks_created = chunks_created
                    progress_item.file_name = os.path.basename(temp_file_path)
                    job['completed_files'] += 1
                    
                    # Clean up temp file
                    if os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
                
                else:
                    progress_item.status = 'failed'
                    progress_item.error = 'Failed to fetch file'
                    job['failed_files'] += 1
            
            except Exception as e:
                progress_item.status = 'failed'
                progress_item.error = str(e)
                job['failed_files'] += 1
                print(f"Error processing {file_id}: {e}")
            
            job['progress'].append(progress_item.dict())
        
        # Update job status
        job['status'] = 'completed' if job['failed_files'] == 0 else 'partial'
        job['completed_at'] = datetime.now().isoformat()
    
    def _fetch_and_save_file(
        self,
        client,
        source_type: DataSourceType,
        file_id: str
    ) -> Optional[str]:
        """
        Fetch file from data source and save to temporary PDF location.
        Returns the temporary file path for processing by existing pipeline.
        """
        try:
            temp_dir = tempfile.gettempdir()
            
            if source_type == DataSourceType.LOCAL_PDF:
                # File is already local, just return the path
                if os.path.exists(file_id):
                    return file_id
                else:
                    print(f"Local file not found: {file_id}")
                    return None
            
            elif source_type == DataSourceType.GDRIVE:
                # Download from Google Drive
                temp_path = os.path.join(temp_dir, f"gdrive_{file_id}_{uuid.uuid4().hex[:8]}.pdf")
                
                # Get file metadata
                file_info = client.service.files().get(
                    fileId=file_id,
                    fields='name,mimeType'
                ).execute()
                
                # Download file
                client.download_file(file_id, temp_path)
                
                return temp_path if os.path.exists(temp_path) else None
            
            elif source_type == DataSourceType.CONFLUENCE:
                # For Confluence, we need to export as PDF or create a temporary document
                # This is a placeholder - you may need to implement HTML to PDF conversion
                print("Warning: Confluence ingestion needs HTML to PDF conversion")
                return None
            
            elif source_type == DataSourceType.JIRA:
                # For JIRA, similar to Confluence - needs export logic
                print("Warning: JIRA ingestion needs export to PDF logic")
                return None
            
            elif source_type == DataSourceType.SHAREPOINT:
                # Download from SharePoint
                temp_path = os.path.join(temp_dir, f"sharepoint_{uuid.uuid4().hex[:8]}.pdf")
                
                file_content = client.download_file(file_id)
                with open(temp_path, 'wb') as f:
                    f.write(file_content)
                
                return temp_path if os.path.exists(temp_path) else None
            
            return None
            
        except Exception as e:
            print(f"Error fetching file {file_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """Get statistics about vector store collections"""
        try:
            text_vectorstore, image_vectorstore = self._get_vector_stores()
            
            # Get text collection stats
            text_collection = text_vectorstore.client.get_collection(
                text_vectorstore.collection_name
            )
            
            # Get image collection stats
            image_collection = image_vectorstore.client.get_collection(
                image_vectorstore.collection_name
            )
            
            return {
                'text_collection': {
                    'name': text_vectorstore.collection_name,
                    'total_vectors': text_collection.points_count,
                    'status': str(text_collection.status)
                },
                'image_collection': {
                    'name': image_vectorstore.collection_name,
                    'total_vectors': image_collection.points_count,
                    'status': str(image_collection.status)
                }
            }
        except Exception as e:
            return {
                'error': str(e)
            }


# Global instance
_vector_store_service = None

def get_vector_store_service() -> VectorStoreService:
    """Get the global vector store service instance"""
    global _vector_store_service
    if _vector_store_service is None:
        _vector_store_service = VectorStoreService()
    return _vector_store_service

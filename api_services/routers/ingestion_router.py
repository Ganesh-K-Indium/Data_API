"""
Ingestion Router - API endpoints for vector database ingestion
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional

try:
    from ..models import (
        IngestionRequest,
        IngestionResponse,
        IngestionStatus,
        DataSourceType
    )
    from ..config import get_connection_manager
    from ..services.vector_store_service import get_vector_store_service
except ImportError:
    from models import (
        IngestionRequest,
        IngestionResponse,
        IngestionStatus,
        DataSourceType
    )
    from config import get_connection_manager
    from services.vector_store_service import get_vector_store_service

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post("/", response_model=IngestionResponse)
async def ingest_files(
    request: IngestionRequest,
    background_tasks: BackgroundTasks
):
    """
    Ingest selected files into vector database using the existing proven pipeline.
    
    The system uses the established pdf_processor1.py pipeline which handles:
    - Text extraction and chunking with deduplication
    - Image extraction with content hashing
    - Automatic ingestion to Qdrant text and image collections
    
    NOTE: Files must be PDF format or convertible to PDF for the pipeline to work.
    The collection_name parameter is ignored - files are ingested into:
    - Text collection: "10K_vector_db"
    - Image collection: "multimodel_vector_db"
    
    Parameters:
    - source_type: Data source type
    - connection_id: Active connection ID
    - file_ids: List of file IDs to ingest
    - metadata: Additional metadata to attach (optional)
    """
    try:
        # Validate connection
        conn_manager = get_connection_manager()
        client = conn_manager.get_client(request.connection_id)
        
        # Create ingestion job
        vector_service = get_vector_store_service()
        response = vector_service.create_ingestion_job(request)
        
        # Process ingestion in background
        background_tasks.add_task(
            vector_service.process_ingestion,
            response.job_id,
            client,
            request.source_type
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(500, f"Failed to create ingestion job: {str(e)}")


@router.get("/status/{job_id}", response_model=IngestionStatus)
async def get_ingestion_status(job_id: str):
    """
    Get the status of an ingestion job
    
    Returns detailed progress information including:
    - Overall job status
    - Number of completed/failed files
    - Per-file progress details
    """
    try:
        vector_service = get_vector_store_service()
        return vector_service.get_job_status(job_id)
    
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to get job status: {str(e)}")


@router.get("/collections/stats")
async def get_all_collection_stats():
    """
    Get statistics about all vector database collections
    
    Returns stats for both text and image collections from the existing vector stores.
    """
    try:
        vector_service = get_vector_store_service()
        stats = vector_service.get_collection_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to get collection stats: {str(e)}")


@router.post("/batch")
async def batch_ingest(
    requests: list[IngestionRequest],
    background_tasks: BackgroundTasks
):
    """
    Create multiple ingestion jobs at once
    
    Useful for ingesting from multiple sources simultaneously.
    Returns a list of job IDs.
    """
    try:
        conn_manager = get_connection_manager()
        vector_service = get_vector_store_service()
        
        job_ids = []
        
        for request in requests:
            # Validate connection
            client = conn_manager.get_client(request.connection_id)
            
            # Create ingestion job
            response = vector_service.create_ingestion_job(request)
            job_ids.append(response.job_id)
            
            # Process in background
            background_tasks.add_task(
                vector_service.process_ingestion,
                response.job_id,
                client,
                request.source_type
            )
        
        return {
            "success": True,
            "job_ids": job_ids,
            "total_jobs": len(job_ids),
            "message": f"Created {len(job_ids)} ingestion jobs"
        }
    
    except Exception as e:
        raise HTTPException(500, f"Failed to create batch ingestion: {str(e)}")

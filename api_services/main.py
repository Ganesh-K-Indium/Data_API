"""
Main FastAPI Application
Data Sources REST API Server
"""
import os
import sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Handle imports - support both running as module and direct execution
try:
    from .models import HealthCheck, DataSourceType, ConnectionStatus
    from .config import get_connection_manager
    from .routers.confluence_router import router as confluence_router
    from .routers.gdrive_router import router as gdrive_router
    from .routers.jira_router import router as jira_router
    from .routers.local_pdf_router import router as local_pdf_router
    from .routers.sharepoint_router import router as sharepoint_router
    from .routers.ingestion_router import router as ingestion_router
except ImportError:
    # Running directly, use absolute imports
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from models import HealthCheck, DataSourceType, ConnectionStatus
    from config import get_connection_manager
    from routers.confluence_router import router as confluence_router
    from routers.gdrive_router import router as gdrive_router
    from routers.jira_router import router as jira_router
    from routers.local_pdf_router import router as local_pdf_router
    from routers.sharepoint_router import router as sharepoint_router
    from routers.ingestion_router import router as ingestion_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown"""
    # Startup
    print("🚀 Starting Data Sources API Server...")
    print("📦 Available data sources: Confluence, Google Drive, JIRA, Local PDF, SharePoint")
    yield
    # Shutdown
    print("👋 Shutting down Data Sources API Server...")


# Initialize FastAPI app
app = FastAPI(
    title="Data Sources API",
    description="REST API for connecting to multiple data sources and ingesting into vector database",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(confluence_router)
app.include_router(gdrive_router)
app.include_router(jira_router)
app.include_router(local_pdf_router)
app.include_router(sharepoint_router)
app.include_router(ingestion_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Data Sources API",
        "version": "1.0.0",
        "description": "REST API for multiple data sources with vector database ingestion",
        "available_sources": [ds.value for ds in DataSourceType],
        "endpoints": {
            "health": "/health",
            "connections": "/connections",
            "confluence": "/confluence/*",
            "gdrive": "/gdrive/*",
            "jira": "/jira/*",
            "local_pdf": "/local-pdf/*",
            "sharepoint": "/sharepoint/*",
            "ingestion": "/ingest/*"
        },
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthCheck, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    conn_manager = get_connection_manager()
    connections = conn_manager.list_connections()
    
    return HealthCheck(
        status="healthy",
        version="1.0.0",
        active_connections=len(connections),
        available_sources=[ds.value for ds in DataSourceType]
    )


@app.get("/connections", tags=["Connections"])
async def list_connections():
    """List all active connections"""
    try:
        conn_manager = get_connection_manager()
        connections = conn_manager.list_connections()
        
        return {
            "success": True,
            "connections": connections,
            "total": len(connections)
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to list connections: {str(e)}")


@app.get("/connections/{connection_id}", tags=["Connections"])
async def get_connection_status(connection_id: str):
    """Get detailed status of a specific connection"""
    try:
        conn_manager = get_connection_manager()
        status = conn_manager.get_connection_status(connection_id)
        
        return {
            "success": True,
            "status": status
        }
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Failed to get connection status: {str(e)}")


@app.delete("/connections/{connection_id}", tags=["Connections"])
async def close_connection(connection_id: str):
    """Close and remove a connection"""
    try:
        conn_manager = get_connection_manager()
        success = conn_manager.close_connection(connection_id)
        
        if success:
            return {
                "success": True,
                "message": f"Connection {connection_id} closed successfully"
            }
        else:
            raise HTTPException(404, f"Connection not found: {connection_id}")
    
    except Exception as e:
        raise HTTPException(500, f"Failed to close connection: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Data Sources API Server")
    print(f"{'='*60}")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"📚 Docs: http://{host}:{port}/docs")
    print(f"🔍 Health: http://{host}:{port}/health")
    print(f"{'='*60}\n")
    
    # Determine the correct module path based on how script is run
    if __package__:
        app_path = "api_services.main:app"
    else:
        app_path = "main:app"
    
    uvicorn.run(
        app_path,
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )

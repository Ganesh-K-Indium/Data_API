"""
Configuration management for API services
Handles connection pooling and credential management
"""
import os
import json
from typing import Dict, Optional, Any
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import uuid

try:
    from .models import DataSourceType, DataSourceConfig
except ImportError:
    from models import DataSourceType, DataSourceConfig

# Load environment variables
load_dotenv()


class ConnectionManager:
    """Manages active connections to data sources"""
    
    def __init__(self):
        self._connections: Dict[str, Dict[str, Any]] = {}
        self._config_file = os.getenv("CONFIG_FILE", "data_sources_config.json")
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if exists"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r') as f:
                    config_data = json.load(f)
                    # Auto-connect to enabled sources
                    for source_config in config_data.get('sources', []):
                        if source_config.get('enabled', False):
                            # Note: Actual connection happens on first use
                            pass
            except Exception as e:
                print(f"Warning: Failed to load config file: {e}")
    
    def create_connection(
        self, 
        source_type: DataSourceType, 
        config: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """
        Create a new connection to a data source
        
        Returns:
            Tuple of (connection_id, metadata)
        """
        connection_id = f"{source_type.value}_{uuid.uuid4().hex[:8]}"
        
        # Store connection info
        self._connections[connection_id] = {
            'source_type': source_type,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'last_used': datetime.now().isoformat(),
            'client': None  # Lazy initialization
        }
        
        # Initialize client
        try:
            client = self._initialize_client(source_type, config)
            self._connections[connection_id]['client'] = client
            
            # Get metadata from client
            metadata = self._get_connection_metadata(source_type, client)
            
            return connection_id, metadata
        except Exception as e:
            # Clean up on failure
            if connection_id in self._connections:
                del self._connections[connection_id]
            raise Exception(f"Failed to initialize {source_type.value} client: {str(e)}")
    
    def _initialize_client(self, source_type: DataSourceType, config: Dict[str, Any]):
        """Initialize the appropriate client based on source type"""
        if source_type == DataSourceType.CONFLUENCE:
            from utils import ConfluenceUtils
            # Set environment variables for ConfluenceUtils
            os.environ['CONFLUENCE_URL'] = config['url']
            os.environ['CONFLUENCE_USERNAME'] = config['username']
            os.environ['CONFLUENCE_API_TOKEN'] = config['api_token']
            if 'cloud' in config:
                os.environ['CONFLUENCE_CLOUD'] = str(config['cloud'])
            return ConfluenceUtils()
        
        elif source_type == DataSourceType.GDRIVE:
            from utils import GoogleDriveClient
            # Handle service account JSON
            if config.get('credentials_type') == 'file_path':
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = config['service_account_json']
            else:
                # Write JSON string to temp file
                temp_file = f"/tmp/gdrive_creds_{uuid.uuid4().hex[:8]}.json"
                with open(temp_file, 'w') as f:
                    f.write(config['service_account_json'])
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = temp_file
            return GoogleDriveClient()
        
        elif source_type == DataSourceType.JIRA:
            from utils import JiraUtils
            os.environ['JIRA_URL'] = config['url']
            os.environ['JIRA_USERNAME'] = config['username']
            os.environ['JIRA_API_TOKEN'] = config['api_token']
            if 'cloud' in config:
                os.environ['JIRA_CLOUD'] = str(config['cloud'])
            return JiraUtils()
        
        elif source_type == DataSourceType.SHAREPOINT:
            from utils import SharePointUtils
            os.environ['SHAREPOINT_SITE_URL'] = config['site_url']
            os.environ['SHAREPOINT_CLIENT_ID'] = config['client_id']
            os.environ['SHAREPOINT_CLIENT_SECRET'] = config['client_secret']
            os.environ['SHAREPOINT_TENANT_ID'] = config['tenant_id']
            return SharePointUtils()
        
        elif source_type == DataSourceType.LOCAL_PDF:
            from utils import LocalPDFUtils
            return LocalPDFUtils(base_directory=config.get('base_directory', './10k_PDFs'))
        
        else:
            raise ValueError(f"Unsupported source type: {source_type}")
    
    def _get_connection_metadata(self, source_type: DataSourceType, client) -> Dict[str, Any]:
        """Get metadata about the connection"""
        metadata = {
            'source_type': source_type.value,
            'connected_at': datetime.now().isoformat()
        }
        
        try:
            if source_type == DataSourceType.CONFLUENCE:
                # Test connection by listing spaces
                spaces = client.confluence_client.get_spaces(limit=1)
                metadata['status'] = 'connected'
                metadata['instance_url'] = client.confluence_client.url
            
            elif source_type == DataSourceType.GDRIVE:
                # Test connection by listing root
                files = client.list_files(folder_id='root', max_results=1)
                metadata['status'] = 'connected'
            
            elif source_type == DataSourceType.JIRA:
                # Test connection
                projects = client.jira_client.projects()
                metadata['status'] = 'connected'
                metadata['project_count'] = len(projects)
            
            elif source_type == DataSourceType.SHAREPOINT:
                metadata['status'] = 'connected'
                metadata['site_url'] = client.site_url
            
            elif source_type == DataSourceType.LOCAL_PDF:
                metadata['status'] = 'connected'
                metadata['base_directory'] = client.base_directory
        
        except Exception as e:
            metadata['status'] = 'error'
            metadata['error'] = str(e)
        
        return metadata
    
    def get_connection(self, connection_id: str):
        """Get an existing connection"""
        if connection_id not in self._connections:
            raise ValueError(f"Connection not found: {connection_id}")
        
        # Update last used time
        self._connections[connection_id]['last_used'] = datetime.now().isoformat()
        
        return self._connections[connection_id]
    
    def get_client(self, connection_id: str):
        """Get the client for a connection"""
        connection = self.get_connection(connection_id)
        return connection['client']
    
    def close_connection(self, connection_id: str):
        """Close and remove a connection"""
        if connection_id in self._connections:
            # Cleanup if needed
            del self._connections[connection_id]
            return True
        return False
    
    def list_connections(self) -> Dict[str, Dict[str, Any]]:
        """List all active connections"""
        return {
            conn_id: {
                'source_type': conn['source_type'].value,
                'created_at': conn['created_at'],
                'last_used': conn['last_used']
            }
            for conn_id, conn in self._connections.items()
        }
    
    def get_connection_status(self, connection_id: str) -> Dict[str, Any]:
        """Get detailed status of a connection"""
        connection = self.get_connection(connection_id)
        return {
            'connection_id': connection_id,
            'source_type': connection['source_type'].value,
            'created_at': connection['created_at'],
            'last_used': connection['last_used'],
            'connected': connection['client'] is not None
        }


# Global connection manager instance
connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return connection_manager

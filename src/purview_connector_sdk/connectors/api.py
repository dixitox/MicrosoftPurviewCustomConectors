"""
API connector for REST APIs
"""

from typing import Dict, Any, List, Optional
import logging
from purview_connector_sdk.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class APIConnector(BaseConnector):
    """
    Connector for REST API sources.
    
    This connector can extract metadata from APIs and create corresponding
    assets in Purview.
    """
    
    def __init__(
        self,
        purview_client,
        api_endpoint: str,
        auth_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize API connector.
        
        Args:
            purview_client: Purview client instance
            api_endpoint: Base API endpoint URL
            auth_config: Authentication configuration
            **kwargs: Additional parameters
        """
        super().__init__(purview_client, **kwargs)
        self.api_endpoint = api_endpoint
        self.auth_config = auth_config or {}
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from API.
        
        Returns:
            Dictionary with API metadata
        """
        logger.info(f"Extracting metadata from API: {self.api_endpoint}")
        
        # Placeholder implementation
        metadata = {
            "api_name": "Sample API",
            "endpoints": [
                {
                    "path": "/users",
                    "method": "GET",
                    "description": "Get all users"
                },
                {
                    "path": "/users/{id}",
                    "method": "GET",
                    "description": "Get user by ID"
                }
            ]
        }
        
        return metadata
    
    def transform_to_atlas(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform API metadata to Atlas entities.
        
        Args:
            metadata: Extracted metadata
            
        Returns:
            List of Atlas entities
        """
        entities = []
        api_name = metadata.get("api_name", "unknown")
        
        # Create API entity
        api_entity = {
            "typeName": "DataSet",
            "attributes": {
                "qualifiedName": self.create_qualified_name(api_name),
                "name": api_name,
                "description": f"API: {api_name}"
            }
        }
        entities.append(api_entity)
        
        logger.info(f"Transformed {len(entities)} entities")
        return entities

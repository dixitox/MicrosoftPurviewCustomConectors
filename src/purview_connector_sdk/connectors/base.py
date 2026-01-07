"""
Base connector class for all Purview connectors
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from purview_connector_sdk.client import PurviewClient
from purview_connector_sdk.exceptions import PurviewConnectorError

logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Abstract base class for Purview connectors.
    
    All custom connectors should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(
        self,
        purview_client: PurviewClient,
        collection_name: Optional[str] = None,
        qualified_name_prefix: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize base connector.
        
        Args:
            purview_client: Purview client instance
            collection_name: Purview collection name for assets
            qualified_name_prefix: Prefix for qualified names
            **kwargs: Additional connector-specific parameters
        """
        self.purview_client = purview_client
        self.collection_name = collection_name or "default"
        self.qualified_name_prefix = qualified_name_prefix or self._generate_prefix()
        self.config = kwargs
        
        logger.info(f"Initialized {self.__class__.__name__}")
    
    def _generate_prefix(self) -> str:
        """Generate qualified name prefix for entities."""
        return f"{self.__class__.__name__.lower()}://"
    
    @abstractmethod
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from the source.
        
        Returns:
            Dictionary containing extracted metadata
        """
        pass
    
    @abstractmethod
    def transform_to_atlas(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform source metadata to Atlas entity format.
        
        Args:
            metadata: Extracted metadata
            
        Returns:
            List of Atlas entity dictionaries
        """
        pass
    
    def validate_entities(self, entities: List[Dict[str, Any]]) -> bool:
        """
        Validate entities before ingestion.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            True if validation passes
        """
        for entity in entities:
            if "typeName" not in entity:
                raise PurviewConnectorError(f"Entity missing typeName: {entity}")
            if "attributes" not in entity:
                raise PurviewConnectorError(f"Entity missing attributes: {entity}")
            if "qualifiedName" not in entity.get("attributes", {}):
                raise PurviewConnectorError(f"Entity missing qualifiedName: {entity}")
        
        return True
    
    def ingest_to_purview(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ingest entities to Purview.
        
        Args:
            entities: List of Atlas entities to ingest
            
        Returns:
            Ingestion results
        """
        self.validate_entities(entities)
        
        logger.info(f"Ingesting {len(entities)} entities to Purview")
        
        # Bulk create entities
        result = self.purview_client.bulk_create_entities(entities)
        
        logger.info(f"Ingestion complete: {result}")
        return result
    
    def scan_and_ingest(self) -> Dict[str, Any]:
        """
        Complete scan workflow: extract, transform, validate, and ingest.
        
        Returns:
            Results dictionary with statistics
        """
        logger.info("Starting scan and ingest workflow")
        
        # Extract metadata
        logger.info("Extracting metadata...")
        metadata = self.extract_metadata()
        
        # Transform to Atlas format
        logger.info("Transforming to Atlas format...")
        entities = self.transform_to_atlas(metadata)
        
        # Ingest to Purview
        logger.info("Ingesting to Purview...")
        result = self.ingest_to_purview(entities)
        
        logger.info("Scan and ingest workflow complete")
        
        return {
            "status": "success",
            "entities_extracted": len(entities),
            "entities_created": result.get("entities_created", 0),
            "metadata": metadata
        }
    
    def create_qualified_name(self, *parts: str) -> str:
        """
        Create a qualified name for an entity.
        
        Args:
            *parts: Parts of the qualified name
            
        Returns:
            Full qualified name
        """
        clean_parts = [str(p).strip("/") for p in parts if p]
        return f"{self.qualified_name_prefix}{'/'.join(clean_parts)}"

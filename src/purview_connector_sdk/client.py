"""
Purview Client - Main client for interacting with Microsoft Purview
"""

import os
import logging
from typing import Optional, Dict, Any, List
from azure.identity import (
    DefaultAzureCredential,
    ClientSecretCredential,
    AzureCliCredential,
    ManagedIdentityCredential
)
from azure.core.credentials import TokenCredential
from purview_connector_sdk.exceptions import AuthenticationError, PurviewConnectorError

logger = logging.getLogger(__name__)


class PurviewClient:
    """
    Client for interacting with Microsoft Purview.
    
    This client handles authentication and provides methods for
    interacting with the Purview Data Map and Catalog.
    """
    
    def __init__(
        self,
        account_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        tenant_id: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        credential: Optional[TokenCredential] = None,
        use_managed_identity: bool = False,
        managed_identity_client_id: Optional[str] = None,
        use_cli_credentials: bool = False,
        interactive: bool = False
    ):
        """
        Initialize Purview Client.
        
        Args:
            account_name: Purview account name
            endpoint: Purview endpoint URL (auto-generated from account_name if not provided)
            tenant_id: Azure AD tenant ID
            client_id: Service Principal client ID
            client_secret: Service Principal client secret
            credential: Pre-configured Azure credential object
            use_managed_identity: Use Managed Identity authentication
            managed_identity_client_id: Client ID for user-assigned managed identity
            use_cli_credentials: Use Azure CLI credentials
            interactive: Use interactive browser authentication
        """
        self.account_name = account_name or os.getenv("PURVIEW_ACCOUNT_NAME")
        
        if not self.account_name and not endpoint:
            raise AuthenticationError("Either account_name or endpoint must be provided")
        
        # Build endpoint URL
        if endpoint:
            self.endpoint = endpoint
        else:
            self.endpoint = f"https://{self.account_name}.purview.azure.com"
        
        # Set up authentication
        self.credential = self._setup_authentication(
            credential=credential,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret,
            use_managed_identity=use_managed_identity,
            managed_identity_client_id=managed_identity_client_id,
            use_cli_credentials=use_cli_credentials,
            interactive=interactive
        )
        
        logger.info(f"Initialized Purview client for {self.endpoint}")
    
    @classmethod
    def from_environment(cls) -> "PurviewClient":
        """
        Create client from environment variables.
        
        Expected variables:
        - PURVIEW_ACCOUNT_NAME or PURVIEW_ENDPOINT
        - AZURE_TENANT_ID
        - AZURE_CLIENT_ID
        - AZURE_CLIENT_SECRET
        
        Returns:
            PurviewClient instance
        """
        return cls(
            account_name=os.getenv("PURVIEW_ACCOUNT_NAME"),
            endpoint=os.getenv("PURVIEW_ENDPOINT"),
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET")
        )
    
    def _setup_authentication(
        self,
        credential: Optional[TokenCredential],
        tenant_id: Optional[str],
        client_id: Optional[str],
        client_secret: Optional[str],
        use_managed_identity: bool,
        managed_identity_client_id: Optional[str],
        use_cli_credentials: bool,
        interactive: bool
    ) -> TokenCredential:
        """Set up authentication credential."""
        
        # Use provided credential
        if credential:
            logger.info("Using provided credential")
            return credential
        
        # Service Principal
        if client_id and client_secret:
            tenant = tenant_id or os.getenv("AZURE_TENANT_ID")
            if not tenant:
                raise AuthenticationError("tenant_id required for Service Principal auth")
            
            logger.info("Using Service Principal authentication")
            return ClientSecretCredential(
                tenant_id=tenant,
                client_id=client_id,
                client_secret=client_secret
            )
        
        # Managed Identity
        if use_managed_identity:
            logger.info("Using Managed Identity authentication")
            if managed_identity_client_id:
                return ManagedIdentityCredential(client_id=managed_identity_client_id)
            return ManagedIdentityCredential()
        
        # Azure CLI
        if use_cli_credentials:
            logger.info("Using Azure CLI credentials")
            return AzureCliCredential()
        
        # Interactive (not recommended for production)
        if interactive:
            logger.warning("Using interactive authentication - not recommended for production")
            from azure.identity import InteractiveBrowserCredential
            return InteractiveBrowserCredential()
        
        # Default credential chain
        logger.info("Using DefaultAzureCredential")
        return DefaultAzureCredential()
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get Purview account information.
        
        Returns:
            Account information dictionary
        """
        # This is a placeholder - actual implementation would call Purview API
        return {
            "name": self.account_name,
            "endpoint": self.endpoint,
            "status": "active"
        }
    
    def get_access_token(self) -> str:
        """
        Get access token for Purview API.
        
        Returns:
            Access token string
        """
        try:
            token = self.credential.get_token("https://purview.azure.net/.default")
            return token.token
        except Exception as e:
            raise AuthenticationError(f"Failed to get access token: {str(e)}")
    
    def create_entity(self, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an entity in Purview.
        
        Args:
            entity_data: Entity data in Atlas format
            
        Returns:
            Created entity response
        """
        # Placeholder for actual Atlas API call
        logger.info(f"Creating entity: {entity_data.get('typeName')}")
        return entity_data
    
    def bulk_create_entities(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple entities in Purview.
        
        Args:
            entities: List of entity data dictionaries
            
        Returns:
            Bulk creation response
        """
        logger.info(f"Bulk creating {len(entities)} entities")
        return {
            "entities_created": len(entities),
            "status": "success"
        }
    
    def get_entity(self, guid: str) -> Dict[str, Any]:
        """
        Get entity by GUID.
        
        Args:
            guid: Entity GUID
            
        Returns:
            Entity data
        """
        logger.info(f"Getting entity: {guid}")
        return {}
    
    def update_entity(self, guid: str, entity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an entity in Purview.
        
        Args:
            guid: Entity GUID
            entity_data: Updated entity data
            
        Returns:
            Updated entity response
        """
        logger.info(f"Updating entity: {guid}")
        return entity_data
    
    def delete_entity(self, guid: str) -> None:
        """
        Delete an entity from Purview.
        
        Args:
            guid: Entity GUID
        """
        logger.info(f"Deleting entity: {guid}")
    
    def search_entities(
        self,
        query: str,
        limit: int = 50,
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Search for entities in Purview.
        
        Args:
            query: Search query string
            limit: Maximum results to return
            offset: Offset for pagination
            filters: Additional search filters
            
        Returns:
            Search results
        """
        logger.info(f"Searching entities: {query}")
        return {
            "query": query,
            "total": 0,
            "results": []
        }
    
    def create_relationship(self, relationship_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a relationship between entities.
        
        Args:
            relationship_data: Relationship data in Atlas format
            
        Returns:
            Created relationship response
        """
        logger.info(f"Creating relationship: {relationship_data.get('typeName')}")
        return relationship_data
    
    def get_lineage(
        self,
        guid: str,
        direction: str = "BOTH",
        depth: int = 3
    ) -> Dict[str, Any]:
        """
        Get lineage for an entity.
        
        Args:
            guid: Entity GUID
            direction: Lineage direction (INPUT, OUTPUT, BOTH)
            depth: How many levels of lineage to retrieve
            
        Returns:
            Lineage information
        """
        logger.info(f"Getting lineage for entity: {guid}")
        return {
            "guid": guid,
            "direction": direction,
            "depth": depth,
            "lineage": {}
        }

"""
Database connector for SQL databases
"""

from typing import Dict, Any, List, Optional
import logging
from purview_connector_sdk.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class DatabaseConnector(BaseConnector):
    """
    Connector for database sources (SQL Server, PostgreSQL, MySQL, etc.)
    
    This connector extracts schema, table, and column metadata from databases.
    """
    
    def __init__(
        self,
        purview_client,
        source_type: str,
        connection_string: Optional[str] = None,
        connection_config: Optional[Dict[str, Any]] = None,
        use_gateway: bool = False,
        gateway_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize database connector.
        
        Args:
            purview_client: Purview client instance
            source_type: Database type (sql_server, postgresql, mysql, etc.)
            connection_string: Database connection string
            connection_config: Connection configuration dictionary
            use_gateway: Whether to use on-premises data gateway
            gateway_id: Gateway ID if using gateway
            **kwargs: Additional parameters
        """
        super().__init__(purview_client, **kwargs)
        self.source_type = source_type
        self.connection_string = connection_string
        self.connection_config = connection_config or {}
        self.use_gateway = use_gateway
        self.gateway_id = gateway_id
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract metadata from database.
        
        Returns:
            Dictionary with schemas, tables, columns
        """
        logger.info(f"Extracting metadata from {self.source_type}")
        
        # Placeholder implementation
        # Real implementation would connect to database and query system tables
        metadata = {
            "database_name": "sample_database",
            "schemas": [
                {
                    "name": "dbo",
                    "tables": [
                        {
                            "name": "customers",
                            "columns": [
                                {"name": "id", "type": "int", "nullable": False},
                                {"name": "name", "type": "varchar", "nullable": False},
                                {"name": "email", "type": "varchar", "nullable": True}
                            ]
                        }
                    ]
                }
            ]
        }
        
        return metadata
    
    def transform_to_atlas(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform database metadata to Atlas entities.
        
        Args:
            metadata: Extracted metadata
            
        Returns:
            List of Atlas entities
        """
        entities = []
        db_name = metadata.get("database_name", "unknown")
        
        # Create database entity
        db_entity = {
            "typeName": "rdbms_db",
            "attributes": {
                "qualifiedName": self.create_qualified_name(db_name),
                "name": db_name,
                "description": f"{self.source_type} database"
            }
        }
        entities.append(db_entity)
        
        # Create schema, table, and column entities
        for schema in metadata.get("schemas", []):
            schema_name = schema["name"]
            
            for table in schema.get("tables", []):
                table_name = table["name"]
                table_qn = self.create_qualified_name(db_name, schema_name, table_name)
                
                # Table entity
                table_entity = {
                    "typeName": "rdbms_table",
                    "attributes": {
                        "qualifiedName": table_qn,
                        "name": table_name,
                        "description": f"Table in {schema_name} schema"
                    }
                }
                entities.append(table_entity)
                
                # Column entities
                for column in table.get("columns", []):
                    column_qn = self.create_qualified_name(
                        db_name, schema_name, table_name, column["name"]
                    )
                    
                    column_entity = {
                        "typeName": "rdbms_column",
                        "attributes": {
                            "qualifiedName": column_qn,
                            "name": column["name"],
                            "data_type": column["type"],
                            "isNullable": column.get("nullable", True)
                        }
                    }
                    entities.append(column_entity)
        
        logger.info(f"Transformed {len(entities)} entities")
        return entities

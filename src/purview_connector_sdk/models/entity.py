"""
Entity models for Purview
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class EntityStatus(Enum):
    """Entity status enumeration"""
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


class EntityType(Enum):
    """Common Atlas entity types"""
    DATASET = "DataSet"
    PROCESS = "Process"
    RDBMS_TABLE = "rdbms_table"
    RDBMS_COLUMN = "rdbms_column"
    RDBMS_DB = "rdbms_db"
    FS_PATH = "fs_path"


@dataclass
class Entity:
    """
    Represents a Purview/Atlas entity.
    """
    type_name: str
    qualified_name: str
    name: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    guid: Optional[str] = None
    status: EntityStatus = EntityStatus.ACTIVE
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    create_time: Optional[int] = None
    update_time: Optional[int] = None
    
    def to_atlas_dict(self) -> Dict[str, Any]:
        """
        Convert entity to Atlas API format.
        
        Returns:
            Dictionary in Atlas format
        """
        atlas_entity = {
            "typeName": self.type_name,
            "attributes": {
                "qualifiedName": self.qualified_name,
                "name": self.name,
                **self.attributes
            },
            "status": self.status.value
        }
        
        if self.guid:
            atlas_entity["guid"] = self.guid
        
        return atlas_entity
    
    @classmethod
    def from_atlas_dict(cls, data: Dict[str, Any]) -> "Entity":
        """
        Create entity from Atlas API response.
        
        Args:
            data: Atlas entity dictionary
            
        Returns:
            Entity instance
        """
        attributes = data.get("attributes", {})
        
        return cls(
            type_name=data.get("typeName", ""),
            qualified_name=attributes.get("qualifiedName", ""),
            name=attributes.get("name", ""),
            attributes={k: v for k, v in attributes.items() 
                       if k not in ["qualifiedName", "name"]},
            guid=data.get("guid"),
            status=EntityStatus(data.get("status", "ACTIVE"))
        )

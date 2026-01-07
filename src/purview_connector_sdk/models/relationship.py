"""
Relationship models for Purview
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class RelationshipStatus(Enum):
    """Relationship status enumeration"""
    ACTIVE = "ACTIVE"
    DELETED = "DELETED"


@dataclass
class Relationship:
    """
    Represents a relationship between two entities in Purview/Atlas.
    """
    type_name: str
    end1_guid: str
    end2_guid: str
    guid: Optional[str] = None
    status: RelationshipStatus = RelationshipStatus.ACTIVE
    attributes: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}
    
    def to_atlas_dict(self) -> Dict[str, Any]:
        """
        Convert relationship to Atlas API format.
        
        Returns:
            Dictionary in Atlas format
        """
        atlas_relationship = {
            "typeName": self.type_name,
            "end1": {"guid": self.end1_guid},
            "end2": {"guid": self.end2_guid},
            "status": self.status.value
        }
        
        if self.guid:
            atlas_relationship["guid"] = self.guid
        
        if self.attributes:
            atlas_relationship["attributes"] = self.attributes
        
        return atlas_relationship
    
    @classmethod
    def from_atlas_dict(cls, data: Dict[str, Any]) -> "Relationship":
        """
        Create relationship from Atlas API response.
        
        Args:
            data: Atlas relationship dictionary
            
        Returns:
            Relationship instance
        """
        return cls(
            type_name=data.get("typeName", ""),
            end1_guid=data.get("end1", {}).get("guid", ""),
            end2_guid=data.get("end2", {}).get("guid", ""),
            guid=data.get("guid"),
            status=RelationshipStatus(data.get("status", "ACTIVE")),
            attributes=data.get("attributes", {})
        )

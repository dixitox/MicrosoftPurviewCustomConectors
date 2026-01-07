"""
File system connector for files and directories
"""

from typing import Dict, Any, List, Optional
import os
import logging
from pathlib import Path
from purview_connector_sdk.connectors.base import BaseConnector

logger = logging.getLogger(__name__)


class FileSystemConnector(BaseConnector):
    """
    Connector for file system sources (local files, network shares, etc.)
    
    This connector scans directories and creates assets for files and folders.
    """
    
    def __init__(
        self,
        purview_client,
        root_path: str,
        file_extensions: Optional[List[str]] = None,
        recursive: bool = True,
        use_gateway: bool = False,
        gateway_id: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize file system connector.
        
        Args:
            purview_client: Purview client instance
            root_path: Root directory path to scan
            file_extensions: List of file extensions to include (e.g., ['.csv', '.xlsx'])
            recursive: Whether to scan subdirectories
            use_gateway: Whether to use on-premises data gateway
            gateway_id: Gateway ID if using gateway
            **kwargs: Additional parameters
        """
        super().__init__(purview_client, **kwargs)
        self.root_path = Path(root_path)
        self.file_extensions = file_extensions
        self.recursive = recursive
        self.use_gateway = use_gateway
        self.gateway_id = gateway_id
    
    def extract_metadata(self) -> Dict[str, Any]:
        """
        Extract file system metadata.
        
        Returns:
            Dictionary with files and directories
        """
        logger.info(f"Scanning file system: {self.root_path}")
        
        files = []
        directories = []
        
        if not self.root_path.exists():
            logger.warning(f"Path does not exist: {self.root_path}")
            return {"files": [], "directories": []}
        
        # Scan directory
        pattern = "**/*" if self.recursive else "*"
        
        for item in self.root_path.glob(pattern):
            # Filter by extension if specified
            if self.file_extensions and item.is_file():
                if item.suffix.lower() not in self.file_extensions:
                    continue
            
            if item.is_file():
                files.append({
                    "name": item.name,
                    "path": str(item),
                    "size": item.stat().st_size,
                    "extension": item.suffix,
                    "modified": item.stat().st_mtime
                })
            elif item.is_dir():
                directories.append({
                    "name": item.name,
                    "path": str(item)
                })
        
        logger.info(f"Found {len(files)} files and {len(directories)} directories")
        
        return {
            "root_path": str(self.root_path),
            "files": files,
            "directories": directories
        }
    
    def transform_to_atlas(self, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Transform file system metadata to Atlas entities.
        
        Args:
            metadata: Extracted metadata
            
        Returns:
            List of Atlas entities
        """
        entities = []
        root_path = metadata.get("root_path", "")
        
        # Create root directory entity
        root_entity = {
            "typeName": "fs_path",
            "attributes": {
                "qualifiedName": self.create_qualified_name(root_path),
                "name": os.path.basename(root_path) or root_path,
                "path": root_path,
                "description": "Root directory"
            }
        }
        entities.append(root_entity)
        
        # Create directory entities
        for directory in metadata.get("directories", []):
            dir_entity = {
                "typeName": "fs_path",
                "attributes": {
                    "qualifiedName": self.create_qualified_name(directory["path"]),
                    "name": directory["name"],
                    "path": directory["path"],
                    "description": "Directory"
                }
            }
            entities.append(dir_entity)
        
        # Create file entities
        for file in metadata.get("files", []):
            file_entity = {
                "typeName": "DataSet",  # Using standard Atlas type
                "attributes": {
                    "qualifiedName": self.create_qualified_name(file["path"]),
                    "name": file["name"],
                    "description": f"File: {file['name']}",
                    "fileExtension": file.get("extension", ""),
                    "fileSize": file.get("size", 0)
                }
            }
            entities.append(file_entity)
        
        logger.info(f"Transformed {len(entities)} entities")
        return entities

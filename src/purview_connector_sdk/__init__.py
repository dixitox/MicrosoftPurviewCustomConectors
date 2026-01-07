"""
Purview Connector SDK - Main Package
A Python SDK for building custom Microsoft Purview connectors
"""

__version__ = "1.0.0"
__author__ = "Microsoft Purview Custom Connectors Team"

from purview_connector_sdk.client import PurviewClient
from purview_connector_sdk.connectors.base import BaseConnector
from purview_connector_sdk.connectors.database import DatabaseConnector
from purview_connector_sdk.connectors.filesystem import FileSystemConnector
from purview_connector_sdk.connectors.api import APIConnector
from purview_connector_sdk.models.entity import Entity, EntityType
from purview_connector_sdk.models.relationship import Relationship
from purview_connector_sdk.exceptions import (
    PurviewConnectorError,
    AuthenticationError,
    IngestionError,
    ValidationError
)

__all__ = [
    # Core client
    "PurviewClient",
    
    # Connectors
    "BaseConnector",
    "DatabaseConnector",
    "FileSystemConnector",
    "APIConnector",
    
    # Models
    "Entity",
    "EntityType",
    "Relationship",
    
    # Exceptions
    "PurviewConnectorError",
    "AuthenticationError",
    "IngestionError",
    "ValidationError",
]

"""
Exception classes for Purview Connector SDK
"""


class PurviewConnectorError(Exception):
    """Base exception for all Purview Connector errors"""
    pass


class AuthenticationError(PurviewConnectorError):
    """Raised when authentication fails"""
    pass


class IngestionError(PurviewConnectorError):
    """Raised when data ingestion fails"""
    pass


class ValidationError(PurviewConnectorError):
    """Raised when data validation fails"""
    pass


class ConnectionError(PurviewConnectorError):
    """Raised when connection to data source fails"""
    pass


class ConfigurationError(PurviewConnectorError):
    """Raised when configuration is invalid"""
    pass


class TransformationError(PurviewConnectorError):
    """Raised when metadata transformation fails"""
    pass

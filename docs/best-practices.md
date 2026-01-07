# Best Practices for Purview Custom Connectors

This guide provides recommendations for building production-ready custom connectors.

## Table of Contents
- [Design Principles](#design-principles)
- [Authentication](#authentication)
- [Performance](#performance)
- [Error Handling](#error-handling)
- [Monitoring](#monitoring)
- [Security](#security)
- [Testing](#testing)

## Design Principles

### 1. Separation of Concerns

Separate extraction, transformation, and ingestion logic:

```python
class MyConnector(BaseConnector):
    def extract_metadata(self):
        """Only extract - no transformation"""
        return raw_metadata
    
    def transform_to_atlas(self, metadata):
        """Only transform - no extraction or ingestion"""
        return atlas_entities
    
    def validate_entities(self, entities):
        """Only validate - don't modify"""
        return is_valid
```

### 2. Idempotency

Ensure operations can be safely retried:

```python
# Use consistent qualified names
qualified_name = f"{source}://{server}/{database}/{table}"

# Always include qualifiedName in entities
entity = {
    "typeName": "rdbms_table",
    "attributes": {
        "qualifiedName": qualified_name,  # Unique identifier
        "name": table_name
    }
}

# Purview will update existing entities with same qualifiedName
```

### 3. Incremental Processing

Track what's been scanned to avoid full rescans:

```python
import json
from datetime import datetime

# Load checkpoint
def load_checkpoint():
    try:
        with open("checkpoint.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"last_scan": None}

# Save checkpoint
def save_checkpoint(timestamp):
    with open("checkpoint.json", "w") as f:
        json.dump({"last_scan": timestamp.isoformat()}, f)

# Use in extraction
checkpoint = load_checkpoint()
last_scan = checkpoint.get("last_scan")

# Only get changes since last scan
metadata = extract_metadata(since=last_scan)

# Save new checkpoint
save_checkpoint(datetime.now())
```

## Authentication

### Use Managed Identity in Azure

```python
# Recommended for Azure resources
client = PurviewClient(
    account_name="my-purview",
    use_managed_identity=True
)
```

### Rotate Secrets Regularly

```python
# Store secrets in Key Vault
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
secret_client = SecretClient(
    vault_url="https://my-vault.vault.azure.net/",
    credential=credential
)

# Retrieve secrets
client_secret = secret_client.get_secret("sp-client-secret").value

# Set up secret rotation alerts (90 days)
```

### Principle of Least Privilege

```bash
# Grant only necessary permissions
az role assignment create \
  --assignee $SP_ID \
  --role "Purview Data Curator" \
  --scope $PURVIEW_RESOURCE_ID

# Don't use Owner or Contributor roles
```

## Performance

### Batch Entity Creation

```python
# Good: Batch create entities
entities = []
for table in tables:
    entities.append(create_table_entity(table))

# Create in batches of 100-500
batch_size = 100
for i in range(0, len(entities), batch_size):
    batch = entities[i:i + batch_size]
    purview_client.bulk_create_entities(batch)
```

```python
# Bad: Create entities one at a time
for table in tables:
    entity = create_table_entity(table)
    purview_client.create_entity(entity)  # Too many API calls!
```

### Use Parallel Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_schema_metadata(schema):
    # Extract metadata for one schema
    return schema_metadata

# Process schemas in parallel
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = {
        executor.submit(extract_schema_metadata, schema): schema
        for schema in schemas
    }
    
    results = []
    for future in as_completed(futures):
        results.append(future.result())
```

### Cache Reference Data

```python
# Cache type definitions
class PurviewClientWithCache(PurviewClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type_cache = {}
    
    def get_type_definition(self, type_name):
        if type_name not in self._type_cache:
            self._type_cache[type_name] = super().get_type_definition(type_name)
        return self._type_cache[type_name]
```

### Optimize Large File Handling

```python
# Use streaming for large files
import ijson

def parse_large_json(file_path):
    with open(file_path, 'rb') as f:
        # Stream parse instead of loading entire file
        for item in ijson.items(f, 'item'):
            yield item

# Process in chunks
for metadata_item in parse_large_json('large_metadata.json'):
    process_item(metadata_item)
```

## Error Handling

### Implement Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def ingest_entities(entities):
    try:
        return purview_client.bulk_create_entities(entities)
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise
```

### Graceful Degradation

```python
def scan_and_ingest(self):
    results = {
        "success": [],
        "failures": [],
        "partial": []
    }
    
    try:
        metadata = self.extract_metadata()
        entities = self.transform_to_atlas(metadata)
        
        # Try to ingest, but don't fail entire scan if some fail
        for entity in entities:
            try:
                result = self.ingest_entity(entity)
                results["success"].append(entity["attributes"]["qualifiedName"])
            except Exception as e:
                logger.error(f"Failed to ingest {entity}: {e}")
                results["failures"].append({
                    "entity": entity,
                    "error": str(e)
                })
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        results["error"] = str(e)
    
    return results
```

### Log Context

```python
import logging
import traceback

logger = logging.getLogger(__name__)

try:
    result = process_entity(entity)
except Exception as e:
    # Log with full context
    logger.error(
        f"Failed to process entity",
        extra={
            "entity_type": entity.get("typeName"),
            "qualified_name": entity.get("attributes", {}).get("qualifiedName"),
            "error": str(e),
            "traceback": traceback.format_exc()
        }
    )
    raise
```

## Monitoring

### Track Key Metrics

```python
from datetime import datetime
import json

class MetricsCollector:
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "entities_scanned": 0,
            "entities_created": 0,
            "entities_updated": 0,
            "entities_failed": 0,
            "errors": []
        }
    
    def start(self):
        self.metrics["start_time"] = datetime.now()
    
    def finish(self):
        self.metrics["end_time"] = datetime.now()
        duration = (self.metrics["end_time"] - self.metrics["start_time"]).total_seconds()
        self.metrics["duration_seconds"] = duration
    
    def record_entity(self, status):
        if status == "created":
            self.metrics["entities_created"] += 1
        elif status == "updated":
            self.metrics["entities_updated"] += 1
        elif status == "failed":
            self.metrics["entities_failed"] += 1
    
    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.metrics, f, indent=2, default=str)

# Usage
metrics = MetricsCollector()
metrics.start()

# ... scanning logic ...

metrics.finish()
metrics.save("/logs/metrics.json")
```

### Set Up Alerts

```python
# Azure Monitor integration
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module

# Configure metrics exporter
exporter = metrics_exporter.new_metrics_exporter(
    connection_string='InstrumentationKey=your-key'
)

# Define measures
entities_processed = measure_module.MeasureInt(
    "entities_processed",
    "Number of entities processed",
    "entities"
)

# Record metrics
stats = stats_module.stats
view_manager = stats.view_manager
view_manager.register_exporter(exporter)

# In your code
measurement_map = stats.stats_recorder.new_measurement_map()
measurement_map.measure_int_put(entities_processed, 100)
measurement_map.record()
```

## Security

### Never Log Secrets

```python
# Bad
logger.info(f"Connecting with password: {password}")

# Good
logger.info("Connecting to database")
```

### Validate Input

```python
def validate_connection_string(conn_str):
    """Validate connection string format"""
    if not conn_str:
        raise ValueError("Connection string cannot be empty")
    
    # Check for SQL injection attempts
    dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", ";--"]
    for keyword in dangerous_keywords:
        if keyword in conn_str.upper():
            raise ValueError(f"Suspicious keyword detected: {keyword}")
    
    return True

# Use validation
conn_str = get_connection_string()
validate_connection_string(conn_str)
```

### Encrypt Sensitive Data

```python
from cryptography.fernet import Fernet

# Generate key (store securely in Key Vault)
key = Fernet.generate_key()
cipher = Fernet(key)

# Encrypt
encrypted_data = cipher.encrypt(sensitive_data.encode())

# Decrypt when needed
decrypted_data = cipher.decrypt(encrypted_data).decode()
```

## Testing

### Unit Tests

```python
import pytest
from purview_connector_sdk import DatabaseConnector

def test_extract_metadata():
    # Mock Purview client
    mock_client = Mock()
    
    connector = DatabaseConnector(
        purview_client=mock_client,
        source_type="sql_server",
        connection_string="mock_conn"
    )
    
    # Test extraction
    metadata = connector.extract_metadata()
    
    assert metadata is not None
    assert "database_name" in metadata
    assert len(metadata["schemas"]) > 0

def test_transform_to_atlas():
    connector = DatabaseConnector(Mock(), "sql_server", "mock_conn")
    
    metadata = {
        "database_name": "testdb",
        "schemas": [{
            "name": "dbo",
            "tables": [{"name": "users", "columns": []}]
        }]
    }
    
    entities = connector.transform_to_atlas(metadata)
    
    assert len(entities) > 0
    assert entities[0]["typeName"] == "rdbms_db"
```

### Integration Tests

```python
@pytest.mark.integration
def test_end_to_end_scan():
    """Test full scan workflow with real Purview"""
    
    # Use test Purview account
    client = PurviewClient(
        account_name=os.getenv("TEST_PURVIEW_ACCOUNT"),
        use_cli_credentials=True
    )
    
    connector = DatabaseConnector(
        purview_client=client,
        source_type="sql_server",
        connection_string=os.getenv("TEST_DB_CONN")
    )
    
    # Run full workflow
    result = connector.scan_and_ingest()
    
    assert result["status"] == "success"
    assert result["entities_created"] > 0
    
    # Cleanup: Delete test entities
    for entity_id in created_entities:
        client.delete_entity(entity_id)
```

### Load Testing

```python
import time
from locust import HttpUser, task, between

class PurviewConnectorLoadTest(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def scan_database(self):
        start_time = time.time()
        
        connector = DatabaseConnector(
            purview_client=self.client,
            source_type="sql_server",
            connection_string=self.conn_str
        )
        
        result = connector.scan_and_ingest()
        
        duration = time.time() - start_time
        
        # Record metrics
        self.environment.events.request_success.fire(
            request_type="scan",
            name="database_scan",
            response_time=duration * 1000,
            response_length=result["entities_created"]
        )
```

## Deployment Checklist

- [ ] All secrets stored in Key Vault
- [ ] Managed Identity enabled
- [ ] Error handling and retry logic implemented
- [ ] Logging configured
- [ ] Metrics and monitoring set up
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] Documentation updated
- [ ] Code reviewed
- [ ] Performance tested
- [ ] Security scan completed

## Additional Resources

- [Getting Started Guide](./getting-started.md)
- [Security Guide](./security.md)
- [Architecture Guide](./architecture.md)
- [Troubleshooting Guide](./troubleshooting.md)

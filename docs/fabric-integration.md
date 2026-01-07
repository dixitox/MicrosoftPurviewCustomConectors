# Microsoft Fabric Integration Guide

This guide explains how to use Microsoft Fabric for orchestrating custom Purview connectors, especially for on-premises and complex data sources.

## Why Microsoft Fabric?

Microsoft Fabric is the recommended platform for Purview custom connectors because:

1. **On-Premises Connectivity**: Built-in Data Gateway support for secure on-prem access
2. **Unified Platform**: Combines data engineering, warehousing, and analytics
3. **Native Integration**: Seamless Purview integration for governance
4. **Serverless Compute**: No infrastructure management required
5. **Future-Proof**: Microsoft's strategic analytics platform

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    On-Premises Environment                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Database   │  │  File Share  │  │  Legacy App  │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼─────────────┘
          │                  │                  │
          └──────────────────┴──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │  Data Gateway    │
                    │  (Self-Hosted)   │
                    └────────┬─────────┘
                             │ HTTPS (Port 443)
                             │
┌────────────────────────────▼─────────────────────────────────┐
│                     Microsoft Fabric                          │
│                                                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Fabric Notebook                         │    │
│  │  ┌───────────────────────────────────────────────┐  │    │
│  │  │  1. Connect via Gateway                       │  │    │
│  │  │  2. Extract Metadata                          │  │    │
│  │  │  3. Transform to Atlas JSON                   │  │    │
│  │  │  4. Validate and Enrich                       │  │    │
│  │  └───────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │              Lakehouse Storage                       │    │
│  │  • Staging area for metadata                        │    │
│  │  • Atlas JSON files                                 │    │
│  │  • Logs and audit trails                           │    │
│  └─────────────────────────────────────────────────────┘    │
│                             │                                 │
│  ┌─────────────────────────▼───────────────────────────┐    │
│  │         Fabric Data Pipeline                         │    │
│  │  • Schedule scans                                    │    │
│  │  • Orchestrate notebooks                            │    │
│  │  • Handle errors & retries                          │    │
│  │  • Trigger Purview ingestion                        │    │
│  └─────────────────────────────────────────────────────┘    │
└───────────────────────────────┬───────────────────────────────┘
                                │ Apache Atlas API
                                ▼
                    ┌───────────────────────┐
                    │  Microsoft Purview    │
                    │  • Data Catalog       │
                    │  • Data Map           │
                    │  • Lineage            │
                    └───────────────────────┘
```

## Prerequisites

- **Microsoft Fabric** capacity (F2 or higher)
- **Fabric Workspace** with appropriate permissions
- **On-Premises Data Gateway** (for on-prem sources)
- **Microsoft Purview** account
- **Service Principal** with permissions

## Setup Steps

### 1. Create Fabric Workspace

1. Go to [Microsoft Fabric Portal](https://app.fabric.microsoft.com)
2. Click **Workspaces** → **New workspace**
3. Enter workspace name: `purview-connectors`
4. Select your Fabric capacity
5. Click **Apply**

### 2. Install On-Premises Data Gateway

For on-premises data sources:

1. **Download the Gateway**
   - Go to [Download Gateway](https://aka.ms/on-premises-data-gateway)
   - Install on a machine in your on-prem network

2. **Configure the Gateway**
   ```powershell
   # After installation, sign in with your Azure account
   # Register the gateway with a name like "OnPrem-Gateway-01"
   ```

3. **Configure in Fabric**
   - Go to Fabric Settings → Manage connections and gateways
   - Find your gateway and verify it's online
   - Create connection to your data source

### 3. Create Lakehouse for Metadata Storage

1. In your workspace, click **New** → **Lakehouse**
2. Name it: `purview_metadata_lake`
3. Create folders:
   ```
   /staging/        # Temporary metadata
   /processed/      # Atlas JSON ready for ingestion
   /logs/          # Execution logs
   /errors/        # Failed ingestion attempts
   ```

### 4. Upload Notebooks

Upload the provided Fabric notebooks to your workspace:

1. Go to your workspace
2. Click **New** → **Import** → **Notebook**
3. Upload notebooks from `./notebooks/fabric/`:
   - `metadata_extractor.ipynb` - Extract metadata from sources
   - `atlas_transformer.ipynb` - Transform to Atlas format
   - `purview_ingestion.ipynb` - Ingest to Purview

### 5. Configure Authentication

#### Create Service Principal

```bash
# Create Service Principal
az ad sp create-for-rbac --name "fabric-purview-connector" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{rg-name}

# Note the output
```

#### Store Credentials in Key Vault

```bash
# Create Key Vault
az keyvault create --name purview-connector-kv \
  --resource-group your-rg \
  --location eastus

# Store secrets
az keyvault secret set --vault-name purview-connector-kv \
  --name "sp-client-id" --value "your-client-id"
az keyvault secret set --vault-name purview-connector-kv \
  --name "sp-client-secret" --value "your-client-secret"
az keyvault secret set --vault-name purview-connector-kv \
  --name "purview-endpoint" --value "https://your-purview.purview.azure.com"
```

#### Link Key Vault to Fabric

1. In Fabric workspace, go to **Settings**
2. Navigate to **Azure Key Vault**
3. Add your Key Vault
4. Grant Fabric Managed Identity access to Key Vault

### 6. Create Data Pipeline

1. In your workspace, click **New** → **Data Pipeline**
2. Name it: `purview-connector-orchestration`
3. Add activities:

```json
{
  "name": "PurviewConnectorPipeline",
  "activities": [
    {
      "name": "ExtractMetadata",
      "type": "FabricNotebook",
      "notebook": "metadata_extractor",
      "parameters": {
        "source_type": "sql_server",
        "connection_name": "OnPremDB"
      }
    },
    {
      "name": "TransformToAtlas",
      "type": "FabricNotebook",
      "notebook": "atlas_transformer",
      "dependsOn": ["ExtractMetadata"]
    },
    {
      "name": "IngestToPurview",
      "type": "FabricNotebook",
      "notebook": "purview_ingestion",
      "dependsOn": ["TransformToAtlas"]
    }
  ],
  "triggers": [
    {
      "name": "DailySchedule",
      "type": "ScheduleTrigger",
      "schedule": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2024-01-01T02:00:00Z"
      }
    }
  ]
}
```

## Sample Fabric Notebook

Here's a sample notebook for extracting metadata:

```python
# Cell 1: Import libraries
from notebookutils import mssparkutils
from purview_connector_sdk import DatabaseConnector, PurviewClient
import json

# Cell 2: Get credentials from Key Vault
client_id = mssparkutils.credentials.getSecret("purview-connector-kv", "sp-client-id")
client_secret = mssparkutils.credentials.getSecret("purview-connector-kv", "sp-client-secret")
purview_endpoint = mssparkutils.credentials.getSecret("purview-connector-kv", "purview-endpoint")

# Cell 3: Initialize Purview client
purview_client = PurviewClient(
    endpoint=purview_endpoint,
    client_id=client_id,
    client_secret=client_secret
)

# Cell 4: Extract metadata via Gateway
# Get parameters from pipeline
source_type = mssparkutils.notebook.getArgument("source_type", "sql_server")
connection_name = mssparkutils.notebook.getArgument("connection_name", "OnPremDB")

# Connect to on-prem database through gateway
connector = DatabaseConnector(
    purview_client=purview_client,
    source_type=source_type,
    connection_name=connection_name,  # Gateway connection
    use_gateway=True
)

# Cell 5: Scan and extract
metadata = connector.extract_metadata()
print(f"Extracted metadata for {len(metadata['entities'])} entities")

# Cell 6: Save to Lakehouse
output_path = f"/lakehouse/default/Files/staging/metadata_{source_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
with open(output_path, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Metadata saved to {output_path}")

# Cell 7: Return results
mssparkutils.notebook.exit({
    "status": "success",
    "entities_count": len(metadata['entities']),
    "output_path": output_path
})
```

## Connecting to On-Premises Sources

### SQL Server Example

```python
# In your Fabric notebook

# Connection configuration (uses gateway)
connection_config = {
    "gateway_id": "your-gateway-id",
    "data_source_id": "your-datasource-id",
    "server": "onprem-sql-server",
    "database": "MyDatabase",
    "authentication": "windows"  # or "sql"
}

# Create connector
from purview_connector_sdk import DatabaseConnector

connector = DatabaseConnector(
    purview_client=purview_client,
    source_type="sql_server",
    connection_config=connection_config,
    use_gateway=True
)

# Extract schema
schemas = connector.get_schemas()
tables = connector.get_tables()
columns = connector.get_columns()

# Transform to Atlas entities
entities = connector.transform_to_atlas(schemas, tables, columns)
```

### File Share Example

```python
# Connect to on-prem file share via gateway
from purview_connector_sdk import FileSystemConnector

connector = FileSystemConnector(
    purview_client=purview_client,
    root_path="\\\\onprem-server\\shared-folder",
    use_gateway=True,
    gateway_id="your-gateway-id"
)

# Scan files
files = connector.scan_files(
    file_extensions=[".csv", ".xlsx", ".parquet"],
    recursive=True
)

# Create assets in Purview
results = connector.ingest_to_purview(files)
```

## Pipeline Scheduling

### Schedule Types

1. **Recurring Schedule**
```json
{
  "schedule": {
    "frequency": "Day",
    "interval": 1,
    "startTime": "2024-01-01T02:00:00Z"
  }
}
```

2. **Tumbling Window** (for incremental processing)
```json
{
  "schedule": {
    "frequency": "Hour",
    "interval": 6,
    "startTime": "2024-01-01T00:00:00Z",
    "endTime": "2024-12-31T23:59:59Z"
  }
}
```

3. **Event-Based Trigger** (on new files)
```json
{
  "type": "BlobEventsTrigger",
  "events": ["Microsoft.Storage.BlobCreated"],
  "blobPathBeginsWith": "/staging/metadata"
}
```

## Monitoring and Logging

### Built-in Monitoring

1. **Pipeline Runs**
   - Go to your workspace → Pipelines
   - View run history, duration, status

2. **Notebook Execution**
   - Click on any notebook
   - View execution history and logs

3. **Gateway Monitoring**
   - Settings → Manage connections and gateways
   - Monitor gateway health and throughput

### Custom Logging

Add logging to your notebooks:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Log to Lakehouse
log_path = f"/lakehouse/default/Files/logs/connector_{datetime.now().strftime('%Y%m%d')}.log"

logger.info(f"Starting metadata extraction for {source_type}")
logger.info(f"Extracted {entity_count} entities")
logger.error(f"Failed to process entity: {entity_id}")
```

## Best Practices

### Performance Optimization
- Use Spark for parallel processing of large metadata sets
- Partition data in Lakehouse by date/source
- Cache frequently accessed reference data
- Use Delta tables for ACID transactions

### Security
- Always use Service Principal, never hardcode credentials
- Store all secrets in Azure Key Vault
- Use Managed Identity when possible
- Implement row-level security in Lakehouse
- Encrypt data at rest and in transit

### Reliability
- Implement retry logic for transient failures
- Use checkpointing for incremental scans
- Maintain idempotent operations
- Log all operations for audit trail
- Set up alerts for pipeline failures

## Troubleshooting

### Gateway Issues

**Issue**: Gateway offline or not responding
```bash
# Check gateway service
Get-Service -Name "PBIEgwService"

# Restart if needed
Restart-Service -Name "PBIEgwService"
```

**Issue**: Cannot connect through gateway
- Verify network connectivity from gateway machine
- Check firewall rules (port 443 outbound)
- Verify data source credentials
- Test connection from gateway machine directly

### Fabric Notebook Issues

**Issue**: Module not found
```python
# Install packages in notebook cell
%pip install pyapacheatlas
%pip install azure-identity
```

**Issue**: Memory errors with large datasets
```python
# Use Spark DataFrame instead of pandas
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
df = spark.read.parquet(metadata_path)
```

## Next Steps

- [Custom Types Guide](./custom-types.md) - Define custom metadata schemas
- [Developer Guide](./developer-guide.md) - Build advanced connectors
- [Best Practices](./best-practices.md) - Production recommendations
- [Examples](../examples/) - Sample connector implementations

## Resources

- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [On-Premises Data Gateway](https://learn.microsoft.com/data-integration/gateway/)
- [Fabric Notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)
- [Fabric Pipelines](https://learn.microsoft.com/fabric/data-factory/pipeline-overview)

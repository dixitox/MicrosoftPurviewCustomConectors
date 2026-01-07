# Deploying to Microsoft Fabric

This guide walks through deploying the Purview Custom Connector Solution to Microsoft Fabric.

## Prerequisites

- **Azure Subscription** with Fabric capacity
- **Microsoft Fabric** license (F2 or higher)
- **Microsoft Purview** account
- **Azure CLI** installed
- **Service Principal** created (see [Authentication Guide](../../docs/authentication.md))

## Deployment Steps

### 1. Create Fabric Workspace

```bash
# Login to Azure
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Variables
WORKSPACE_NAME="purview-connectors"
LOCATION="eastus"
```

You can create workspace via:
- [Fabric Portal](https://app.fabric.microsoft.com)
- PowerShell
- Azure CLI (if available in your tenant)

### 2. Create Lakehouse

In your Fabric workspace:

1. Click **New** → **Lakehouse**
2. Name: `purview_metadata_lake`
3. Create folders structure:

```bash
# Folder structure
/staging/             # Raw metadata from sources
/processed/           # Transformed Atlas JSON
/logs/               # Execution logs
/errors/             # Failed ingestion attempts
/archive/            # Historical data
/checkpoints/        # Scan checkpoints
```

### 3. Upload Notebooks

Upload the provided notebooks from `./notebooks/fabric/`:

```bash
# From your local machine
# Navigate to notebooks folder
cd ../../notebooks/fabric/

# Upload via Fabric UI or REST API
# Files to upload:
# - metadata_extractor.ipynb
# - atlas_transformer.ipynb
# - purview_ingestion.ipynb
```

Or use the Fabric REST API:

```python
import requests
import json

# Get access token
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
token = credential.get_token("https://api.fabric.microsoft.com/.default")

# Upload notebook
workspace_id = "your-workspace-id"
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}

with open("metadata_extractor.ipynb", "r") as f:
    notebook_content = json.load(f)

response = requests.post(
    f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks",
    headers=headers,
    json={
        "displayName": "metadata_extractor",
        "definition": notebook_content
    }
)
```

### 4. Configure Authentication

#### Option A: Managed Identity (Recommended)

Enable Managed Identity on Fabric:

```bash
# Fabric workspace has Managed Identity by default
# Get the workspace identity principal ID
WORKSPACE_ID="your-workspace-id"

# Grant Purview permissions
PURVIEW_RESOURCE_ID="/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Purview/accounts/{purview-account}"

az role assignment create \
  --assignee $WORKSPACE_ID \
  --role "Purview Data Curator" \
  --scope $PURVIEW_RESOURCE_ID
```

#### Option B: Service Principal with Key Vault

```bash
# Create Key Vault
KV_NAME="purview-connector-kv"
RG_NAME="your-resource-group"

az keyvault create \
  --name $KV_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION

# Store Service Principal credentials
az keyvault secret set \
  --vault-name $KV_NAME \
  --name "sp-client-id" \
  --value "your-client-id"

az keyvault secret set \
  --vault-name $KV_NAME \
  --name "sp-client-secret" \
  --value "your-client-secret"

az keyvault secret set \
  --vault-name $KV_NAME \
  --name "sp-tenant-id" \
  --value "your-tenant-id"

az keyvault secret set \
  --vault-name $KV_NAME \
  --name "purview-endpoint" \
  --value "https://your-purview.purview.azure.com"

# Grant Fabric workspace access to Key Vault
az keyvault set-policy \
  --name $KV_NAME \
  --object-id $WORKSPACE_ID \
  --secret-permissions get list
```

### 5. Install On-Premises Data Gateway (If Needed)

For on-premises data sources:

#### Windows Installation

```powershell
# Download installer
$gatewayUrl = "https://aka.ms/on-premises-data-gateway"
Invoke-WebRequest -Uri $gatewayUrl -OutFile "gateway-installer.exe"

# Run installer
.\gateway-installer.exe

# After installation, configure gateway
# Sign in with Azure account
# Register gateway with name: "OnPrem-Gateway-01"
```

#### Linux Installation (Beta)

```bash
# Add Microsoft package repository
wget -q https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb

# Install gateway
sudo apt-get update
sudo apt-get install -y on-premises-data-gateway

# Configure gateway
sudo /opt/microsoft/on-premises-data-gateway/GatewayConfigurator.sh
```

#### Register Gateway in Fabric

```bash
# Via Fabric UI:
# Settings → Manage connections and gateways
# Add new gateway connection
# Select your registered gateway
# Add data source connection
```

### 6. Create and Configure Pipeline

Create a new pipeline in Fabric:

```json
{
  "name": "PurviewConnectorOrchestration",
  "properties": {
    "activities": [
      {
        "name": "ExtractMetadata",
        "type": "FabricNotebook",
        "dependsOn": [],
        "policy": {
          "timeout": "0.12:00:00",
          "retry": 2,
          "retryIntervalInSeconds": 30
        },
        "typeProperties": {
          "notebook": {
            "referenceName": "metadata_extractor",
            "type": "NotebookReference"
          },
          "parameters": {
            "source_type": {
              "value": "@pipeline().parameters.source_type",
              "type": "Expression"
            },
            "connection_name": {
              "value": "@pipeline().parameters.connection_name",
              "type": "Expression"
            }
          }
        }
      },
      {
        "name": "TransformToAtlas",
        "type": "FabricNotebook",
        "dependsOn": [
          {
            "activity": "ExtractMetadata",
            "dependencyConditions": ["Succeeded"]
          }
        ],
        "typeProperties": {
          "notebook": {
            "referenceName": "atlas_transformer",
            "type": "NotebookReference"
          },
          "parameters": {
            "metadata_path": {
              "value": "@activity('ExtractMetadata').output.metadata_path",
              "type": "Expression"
            }
          }
        }
      },
      {
        "name": "IngestToPurview",
        "type": "FabricNotebook",
        "dependsOn": [
          {
            "activity": "TransformToAtlas",
            "dependencyConditions": ["Succeeded"]
          }
        ],
        "typeProperties": {
          "notebook": {
            "referenceName": "purview_ingestion",
            "type": "NotebookReference"
          },
          "parameters": {
            "atlas_json_path": {
              "value": "@activity('TransformToAtlas').output.atlas_json_path",
              "type": "Expression"
            }
          }
        }
      }
    ],
    "parameters": {
      "source_type": {
        "type": "String",
        "defaultValue": "sql_server"
      },
      "connection_name": {
        "type": "String",
        "defaultValue": "OnPremDB"
      }
    }
  }
}
```

Save as `pipeline.json` and import via Fabric UI or API.

### 7. Configure Pipeline Triggers

#### Schedule Trigger (Daily at 2 AM)

```json
{
  "name": "DailySchedule",
  "properties": {
    "type": "ScheduleTrigger",
    "typeProperties": {
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2024-01-01T02:00:00Z",
        "timeZone": "UTC"
      }
    },
    "pipelines": [
      {
        "pipelineReference": {
          "referenceName": "PurviewConnectorOrchestration",
          "type": "PipelineReference"
        },
        "parameters": {
          "source_type": "sql_server",
          "connection_name": "ProductionDB"
        }
      }
    ]
  }
}
```

#### Event-Based Trigger (On New Files)

```json
{
  "name": "OnNewMetadataFile",
  "properties": {
    "type": "BlobEventsTrigger",
    "typeProperties": {
      "blobPathBeginsWith": "/lakehouse/metadata_lake/Files/staging/",
      "events": ["Microsoft.Storage.BlobCreated"]
    },
    "pipelines": [
      {
        "pipelineReference": {
          "referenceName": "PurviewConnectorOrchestration",
          "type": "PipelineReference"
        }
      }
    ]
  }
}
```

## Verification

### Test the Pipeline

1. **Manual Trigger**
   ```bash
   # Via Fabric UI: Click "Run" on pipeline
   # Or via API:
   curl -X POST \
     "https://api.fabric.microsoft.com/v1/workspaces/{workspace-id}/pipelines/{pipeline-id}/run" \
     -H "Authorization: Bearer {token}"
   ```

2. **Monitor Execution**
   - Go to Fabric workspace → Pipelines
   - Click on pipeline name
   - View run history

3. **Check Results**
   - Verify entities created in Purview
   - Check Lakehouse for output files
   - Review logs for errors

### Validate in Purview

```bash
# Login to Purview portal
# https://web.purview.azure.com

# Navigate to:
# Data Catalog → Browse Assets
# Select your collection
# Verify entities are present
```

## Troubleshooting

### Pipeline Failures

**Check notebook output:**
```python
# In notebook cell
try:
    # Your code
    result = scan_and_ingest()
except Exception as e:
    # Log detailed error
    logger.error(f"Error: {str(e)}", exc_info=True)
    raise
```

**View execution logs:**
- Fabric UI → Pipeline runs → Click run → View logs
- Lakehouse → Files → logs folder

### Gateway Issues

```bash
# Check gateway status
# Windows PowerShell:
Get-Service -Name "PBIEgwService"

# View gateway logs
# Location: C:\Program Files\On-premises data gateway\GatewayLogs\
```

### Authentication Errors

```python
# Test Purview connection
from azure.identity import DefaultAzureCredential
from azure.purview.catalog import PurviewCatalogClient

credential = DefaultAzureCredential()
client = PurviewCatalogClient(
    endpoint="https://your-purview.purview.azure.com",
    credential=credential
)

# Test API call
try:
    types = client.types.get_all_type_definitions()
    print("✓ Successfully connected to Purview")
except Exception as e:
    print(f"✗ Connection failed: {e}")
```

## Next Steps

- [Configure additional data sources](../../docs/getting-started.md)
- [Add custom types](../../docs/custom-types.md)
- [Implement lineage tracking](../../docs/lineage.md)
- [Set up monitoring](../../docs/monitoring.md)

## Resources

- [Fabric Documentation](https://learn.microsoft.com/fabric/)
- [Purview Documentation](https://learn.microsoft.com/azure/purview/)
- [Data Gateway Documentation](https://learn.microsoft.com/data-integration/gateway/)

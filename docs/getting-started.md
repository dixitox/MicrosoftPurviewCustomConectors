# Getting Started Guide

This guide will walk you through setting up and using the Microsoft Purview Custom Connector Solution Accelerator.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Authentication Setup](#authentication-setup)
- [Your First Connector](#your-first-connector)
- [Next Steps](#next-steps)

## Prerequisites

Before you begin, ensure you have:

### Azure Resources
- **Azure Subscription** with Owner or Contributor role
- **Microsoft Purview** account (create one if needed)
- **Microsoft Fabric** workspace (recommended) OR Azure Synapse workspace

### Local Development Environment
- **Python 3.8 or higher** installed
- **Git** for version control
- **Visual Studio Code** or your preferred IDE
- **Azure CLI** installed and configured

### Permissions
- **Data Curator** role in Purview
- **Contributor** role in the resource group containing Fabric/Synapse
- Permission to create **Service Principals** in Azure AD

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/dixitox/MicrosoftPurviewCustomConectors.git
cd MicrosoftPurviewCustomConectors
```

### 2. Set Up Python Environment

Create a virtual environment and install dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Install the SDK

```bash
# Install the Purview Connector SDK
pip install -e ./src/purview_connector_sdk
```

## Authentication Setup

### Option 1: Service Principal (Recommended for Production)

1. **Create a Service Principal**

```bash
az ad sp create-for-rbac --name "purview-connector-sp" --role Contributor
```

Save the output:
- `appId` (Client ID)
- `password` (Client Secret)
- `tenant` (Tenant ID)

2. **Grant Purview Permissions**

Go to Azure Portal → Purview Account → Access Control (IAM):
- Add role assignment: **Data Curator**
- Select the service principal created above

3. **Store Credentials Securely**

Create a `.env` file (already in `.gitignore`):

```bash
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
PURVIEW_ACCOUNT_NAME=your-purview-account
PURVIEW_ENDPOINT=https://your-purview-account.purview.azure.com
```

### Option 2: Managed Identity (For Azure Resources)

If running from Azure (Fabric, Synapse, VM):

1. Enable Managed Identity on your Azure resource
2. Grant the Managed Identity **Data Curator** role in Purview
3. No credentials needed - authentication is automatic

### Option 3: Azure CLI (For Local Development/Testing)

```bash
az login
az account set --subscription "your-subscription-id"
```

## Your First Connector

Let's create a simple file system connector to scan a local directory.

### 1. Create a Connector Script

Create `my_first_connector.py`:

```python
from purview_connector_sdk import FileSystemConnector, PurviewClient

# Initialize Purview client
purview = PurviewClient(
    account_name="your-purview-account",
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Create connector
connector = FileSystemConnector(
    purview_client=purview,
    root_path="./sample_data",
    collection_name="MyFirstCollection"
)

# Scan and ingest
print("Starting scan...")
results = connector.scan_and_ingest()
print(f"Ingested {results['entities_created']} entities")
print(f"Scan complete!")
```

### 2. Create Sample Data

```bash
mkdir sample_data
echo "id,name,email" > sample_data/users.csv
echo "1,John Doe,john@example.com" >> sample_data/users.csv
echo "Sample document content" > sample_data/readme.txt
```

### 3. Run the Connector

```bash
python my_first_connector.py
```

### 4. Verify in Purview

1. Open Azure Portal → Your Purview Account
2. Go to **Data Catalog** → **Browse Assets**
3. Navigate to your collection
4. You should see the scanned files!

## Next Steps

### Explore Examples

Check out the example connectors:
- [Database Connector](../examples/database-connector/README.md) - Connect to SQL databases
- [File Connector](../examples/file-connector/README.md) - Advanced file scanning
- [API Connector](../examples/api-connector/README.md) - Integrate REST APIs
- [ETL Lineage](../examples/etl-lineage/README.md) - Track data lineage

### Deploy to Microsoft Fabric

For production deployments, use Microsoft Fabric:
1. See [Fabric Integration Guide](./fabric-integration.md)
2. Follow [Deployment Guide](../deployment/fabric/README.md)

### Customize Your Connector

- **Define custom types**: See [Custom Types Guide](./custom-types.md)
- **Add metadata extraction**: See [Developer Guide](./developer-guide.md)
- **Implement lineage**: See [Lineage Guide](./lineage.md)

### Advanced Topics

- [Best Practices](./best-practices.md) - Production recommendations
- [Security Guide](./security.md) - Security hardening
- [Performance Tuning](./performance.md) - Optimization tips
- [Troubleshooting](./troubleshooting.md) - Common issues

## Common Issues

### Issue: "Authentication failed"

**Solution**: Verify your credentials and permissions:
```bash
az login
az account show
# Check if you have access to Purview
```

### Issue: "Module not found"

**Solution**: Ensure virtual environment is activated and dependencies installed:
```bash
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Cannot connect to Purview"

**Solution**: Check network connectivity and firewall rules:
- Verify Purview endpoint is correct
- Check if firewall allows outbound HTTPS traffic
- Verify Service Principal has Data Curator role

## Getting Help

- **Documentation**: Browse the [docs](.) folder
- **Examples**: Check the [examples](../examples) folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/dixitox/MicrosoftPurviewCustomConectors/issues)
- **Discussions**: Ask questions on [GitHub Discussions](https://github.com/dixitox/MicrosoftPurviewCustomConectors/discussions)

## Useful Resources

- [Microsoft Purview Documentation](https://docs.microsoft.com/azure/purview/)
- [Apache Atlas Documentation](https://atlas.apache.org/)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/fabric/)
- [PyApacheAtlas Library](https://github.com/wjohnson/pyapacheatlas)

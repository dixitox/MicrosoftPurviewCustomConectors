# Authentication Guide

This guide covers authentication options for Microsoft Purview Custom Connectors.

## Authentication Methods

### 1. Service Principal (Recommended for Production)

Service Principals provide secure, automated authentication for production environments.

#### Creating a Service Principal

```bash
# Create Service Principal
az ad sp create-for-rbac \
  --name "purview-connector-sp" \
  --role Contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}

# Output will include:
# - appId (Client ID)
# - password (Client Secret)
# - tenant (Tenant ID)
```

#### Grant Purview Permissions

The Service Principal needs appropriate permissions:

1. **Data Curator** - Can create and manage assets
2. **Data Reader** - Can read metadata (minimum for read-only connectors)
3. **Data Source Administrator** - Can register and scan data sources

Grant permissions via Azure Portal:

```bash
# Or via CLI
az role assignment create \
  --assignee {client-id} \
  --role "Purview Data Curator" \
  --scope /subscriptions/{subscription-id}/resourceGroups/{rg}/providers/Microsoft.Purview/accounts/{purview-account}
```

#### Using Service Principal in Code

```python
from purview_connector_sdk import PurviewClient

# Using explicit credentials
client = PurviewClient(
    account_name="your-purview-account",
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# Using environment variables
# Set: AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
client = PurviewClient.from_environment()
```

### 2. Managed Identity (Recommended for Azure Resources)

Managed Identities eliminate the need to manage credentials.

#### System-Assigned Managed Identity

Enable on your Azure resource (VM, Fabric, Synapse):

```bash
# For VM
az vm identity assign --name myVM --resource-group myRG

# For Synapse
az synapse workspace identity assign --name mySynapse --resource-group myRG
```

Grant Purview permissions:

```bash
# Get the managed identity principal ID
PRINCIPAL_ID=$(az vm identity show --name myVM --resource-group myRG --query principalId -o tsv)

# Grant permissions
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Purview Data Curator" \
  --scope /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Purview/accounts/{purview}
```

#### Using Managed Identity in Code

```python
from purview_connector_sdk import PurviewClient

# Automatically uses Managed Identity when running in Azure
client = PurviewClient(
    account_name="your-purview-account",
    use_managed_identity=True
)
```

#### User-Assigned Managed Identity

For more control:

```bash
# Create managed identity
az identity create --name purview-connector-identity --resource-group myRG

# Assign to resource
az vm identity assign \
  --name myVM \
  --resource-group myRG \
  --identities /subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/purview-connector-identity
```

```python
# Use specific client ID
client = PurviewClient(
    account_name="your-purview-account",
    managed_identity_client_id="your-managed-identity-client-id"
)
```

### 3. Azure CLI (For Local Development)

Simplest option for local testing:

```bash
# Login
az login

# Set subscription
az account set --subscription "your-subscription-id"

# Verify
az account show
```

```python
from purview_connector_sdk import PurviewClient

# Uses current Azure CLI credentials
client = PurviewClient(
    account_name="your-purview-account",
    use_cli_credentials=True
)
```

### 4. Interactive Browser (Development Only)

For testing in interactive environments:

```python
from purview_connector_sdk import PurviewClient

# Opens browser for authentication
client = PurviewClient(
    account_name="your-purview-account",
    interactive=True
)
```

## Storing Credentials Securely

### Azure Key Vault (Recommended)

```bash
# Create Key Vault
az keyvault create \
  --name purview-connector-kv \
  --resource-group myRG \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name purview-connector-kv \
  --name "sp-client-id" \
  --value "your-client-id"

az keyvault secret set \
  --vault-name purview-connector-kv \
  --name "sp-client-secret" \
  --value "your-client-secret"

az keyvault secret set \
  --vault-name purview-connector-kv \
  --name "sp-tenant-id" \
  --value "your-tenant-id"
```

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Get credentials from Key Vault
credential = DefaultAzureCredential()
secret_client = SecretClient(
    vault_url="https://purview-connector-kv.vault.azure.net/",
    credential=credential
)

client_id = secret_client.get_secret("sp-client-id").value
client_secret = secret_client.get_secret("sp-client-secret").value
tenant_id = secret_client.get_secret("sp-tenant-id").value

# Use in Purview client
from purview_connector_sdk import PurviewClient

client = PurviewClient(
    account_name="your-purview-account",
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)
```

### Environment Variables

For local development:

```bash
# .env file (add to .gitignore!)
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
PURVIEW_ACCOUNT_NAME=your-purview-account
```

```python
import os
from dotenv import load_dotenv
from purview_connector_sdk import PurviewClient

# Load environment variables
load_dotenv()

# Use in client
client = PurviewClient(
    account_name=os.getenv("PURVIEW_ACCOUNT_NAME"),
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    client_id=os.getenv("AZURE_CLIENT_ID"),
    client_secret=os.getenv("AZURE_CLIENT_SECRET")
)
```

## Required Permissions

### Purview Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| Data Reader | Read metadata | Read-only connectors |
| Data Curator | Create/update/delete assets | Standard connectors |
| Data Source Administrator | Manage data sources and scans | Full connector management |

### Azure Resource Permissions

For data source access:

- **SQL Database**: `db_datareader` or higher
- **Storage Account**: `Storage Blob Data Reader`
- **Key Vault**: `Key Vault Secrets User`
- **Data Gateway**: Gateway user access

## Multi-Tenant Scenarios

For connecting to Purview in different tenant:

```python
from purview_connector_sdk import PurviewClient

# Specify tenant explicitly
client = PurviewClient(
    account_name="purview-in-tenant-b",
    tenant_id="tenant-b-id",
    client_id="app-id-in-tenant-b",
    client_secret="secret",
    authority_host="https://login.microsoftonline.com/tenant-b-id"
)
```

## Troubleshooting

### Common Issues

#### "AADSTS700016: Application not found"
- Verify client ID is correct
- Check if Service Principal exists in correct tenant
- Ensure app registration is not deleted

#### "AADSTS7000215: Invalid client secret"
- Client secret may be expired
- Create new secret in Azure Portal → App Registrations
- Update your configuration

#### "Insufficient privileges"
- Check RBAC role assignments
- Verify Service Principal has Data Curator role
- May take a few minutes for permissions to propagate

### Testing Authentication

```python
from purview_connector_sdk import PurviewClient

try:
    client = PurviewClient(
        account_name="your-purview-account",
        tenant_id="your-tenant-id",
        client_id="your-client-id",
        client_secret="your-client-secret"
    )
    
    # Test connection
    account_info = client.get_account_info()
    print(f"✓ Connected to Purview: {account_info['name']}")
    
except Exception as e:
    print(f"✗ Authentication failed: {str(e)}")
```

## Best Practices

1. **Use Managed Identity** when running in Azure
2. **Use Service Principal** for non-Azure or cross-tenant scenarios
3. **Never commit credentials** to source control
4. **Rotate secrets regularly** (every 90 days recommended)
5. **Use separate principals** for dev/test/prod
6. **Apply least privilege** - only grant necessary permissions
7. **Monitor authentication** - enable Azure AD sign-in logs
8. **Use Key Vault** for production secrets

## Security Checklist

- [ ] Credentials stored in Key Vault or secure secret management
- [ ] `.env` files added to `.gitignore`
- [ ] Service Principal has minimum required permissions
- [ ] Secret rotation policy in place
- [ ] Audit logging enabled
- [ ] Multi-factor authentication enabled for interactive access
- [ ] Conditional access policies configured
- [ ] Regular access reviews scheduled

## Next Steps

- [Getting Started Guide](./getting-started.md) - Setup your first connector
- [Security Guide](./security.md) - Additional security hardening
- [Fabric Integration](./fabric-integration.md) - Use Managed Identity with Fabric
- [Best Practices](./best-practices.md) - Production recommendations

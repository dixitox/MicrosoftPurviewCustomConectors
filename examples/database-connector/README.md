# Database Connector Example

This example demonstrates how to create a custom connector for SQL databases using the Purview Connector SDK.

## Overview

The database connector extracts metadata from SQL databases (SQL Server, PostgreSQL, MySQL) and ingests it into Microsoft Purview, creating assets for:
- Databases
- Schemas
- Tables
- Columns
- Relationships between entities

## Prerequisites

- Microsoft Purview account
- Access to a SQL database
- Python 3.8+
- Required packages installed

## Installation

```bash
# Install SDK with database support
pip install -e ../../src/purview_connector_sdk[database]

# Or install specific database driver
pip install pyodbc  # For SQL Server
pip install pymysql  # For MySQL
pip install psycopg2-binary  # For PostgreSQL
```

## Configuration

Create a `.env` file:

```env
# Purview Configuration
PURVIEW_ACCOUNT_NAME=your-purview-account
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Database Configuration
DB_TYPE=sql_server  # or postgresql, mysql
DB_SERVER=your-server.database.windows.net
DB_NAME=your-database
DB_USER=your-username
DB_PASSWORD=your-password
```

## Usage

### Basic Example

```python
from purview_connector_sdk import PurviewClient, DatabaseConnector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Purview client
purview_client = PurviewClient.from_environment()

# Create database connector
connector = DatabaseConnector(
    purview_client=purview_client,
    source_type=os.getenv("DB_TYPE"),
    connection_string=f"Driver={{ODBC Driver 17 for SQL Server}};"
                     f"Server={os.getenv('DB_SERVER')};"
                     f"Database={os.getenv('DB_NAME')};"
                     f"UID={os.getenv('DB_USER')};"
                     f"PWD={os.getenv('DB_PASSWORD')}"
)

# Scan and ingest
results = connector.scan_and_ingest()
print(f"Ingested {results['entities_created']} entities")
```

### Advanced Example with Gateway

For on-premises databases using Microsoft Fabric:

```python
from purview_connector_sdk import PurviewClient, DatabaseConnector

# Using Managed Identity (in Fabric)
purview_client = PurviewClient(
    account_name="your-purview-account",
    use_managed_identity=True
)

# Connect via on-premises gateway
connector = DatabaseConnector(
    purview_client=purview_client,
    source_type="sql_server",
    connection_config={
        "gateway_id": "your-gateway-id",
        "server": "onprem-sql-server",
        "database": "MyDatabase",
        "authentication": "windows"
    },
    use_gateway=True,
    collection_name="OnPremDatabases"
)

# Extract metadata
metadata = connector.extract_metadata()
print(f"Found {len(metadata['schemas'])} schemas")

# Transform and ingest
entities = connector.transform_to_atlas(metadata)
results = connector.ingest_to_purview(entities)
```

## Customization

### Custom Entity Types

Define custom types for your database:

```python
# Define custom column type with additional attributes
custom_column = {
    "typeName": "custom_db_column",
    "attributes": {
        "qualifiedName": "mydb://schema/table/column",
        "name": "customer_id",
        "data_type": "varchar(50)",
        "isNullable": False,
        "isPrimaryKey": True,
        "isForeignKey": False,
        "defaultValue": None,
        "description": "Customer unique identifier"
    }
}
```

### Incremental Scanning

Track last scan time and only process changes:

```python
from datetime import datetime
import json

# Load last scan timestamp
try:
    with open("last_scan.json", "r") as f:
        last_scan = json.load(f)
        last_scan_time = datetime.fromisoformat(last_scan["timestamp"])
except FileNotFoundError:
    last_scan_time = None

# Extract only changed metadata
metadata = connector.extract_metadata(since=last_scan_time)

# Save current scan time
with open("last_scan.json", "w") as f:
    json.dump({"timestamp": datetime.now().isoformat()}, f)
```

## Running the Example

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the example
python database_connector_example.py
```

## Supported Databases

- **SQL Server** - Azure SQL, SQL Server 2016+
- **PostgreSQL** - 9.6+
- **MySQL** - 5.7+
- **Oracle** - 12c+ (requires cx_Oracle)
- **Snowflake** - (requires snowflake-connector-python)

## Troubleshooting

### Connection Issues

**Error**: "Cannot connect to database"
- Verify connection string
- Check firewall rules
- Ensure database credentials are correct
- Test connection using database client tools

**Error**: "Driver not found"
```bash
# Install ODBC driver for SQL Server
# Ubuntu/Debian
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install msodbcsql17

# Windows - download from Microsoft
```

### Authentication Issues

**Error**: "Login failed"
- Check username and password
- Verify SQL Server authentication is enabled
- Check user has appropriate permissions

**Required Permissions**:
- `db_datareader` on target database
- Access to system catalog views (`sys.schemas`, `sys.tables`, `sys.columns`)

## Next Steps

- [Advanced Database Connector](./advanced_example.md)
- [Custom Type Definition](../../docs/custom-types.md)
- [Lineage Tracking](../etl-lineage/README.md)
- [Fabric Integration](../../docs/fabric-integration.md)

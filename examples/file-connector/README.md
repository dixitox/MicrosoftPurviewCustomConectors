# File System Connector Example

This example demonstrates how to create a custom connector for file systems using the Purview Connector SDK.

## Overview

The file system connector scans directories and creates Purview assets for:
- Files (CSV, Excel, JSON, Parquet, etc.)
- Directories/Folders
- File metadata (size, type, last modified)

## Use Cases

- **Data Lake Scanning**: Catalog files in Azure Data Lake or Blob Storage
- **Network Share Discovery**: Inventory files on network file shares
- **On-Premises File Systems**: Scan local directories via data gateway

## Prerequisites

- Microsoft Purview account
- Access to file system or storage account
- Python 3.8+
- Purview Connector SDK installed

## Installation

```bash
# Install SDK
pip install -e ../../src/purview_connector_sdk

# Install file parsing libraries (optional)
pip install openpyxl python-docx PyPDF2
```

## Configuration

Create a `.env` file:

```env
# Purview Configuration
PURVIEW_ACCOUNT_NAME=your-purview-account
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# File System Configuration
ROOT_PATH=/path/to/scan
RECURSIVE=true
FILE_EXTENSIONS=.csv,.xlsx,.json,.parquet
COLLECTION_NAME=FileAssets
```

## Usage

### Basic Example - Local Files

```python
from purview_connector_sdk import PurviewClient, FileSystemConnector
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Initialize Purview client
purview_client = PurviewClient.from_environment()

# Create file system connector
connector = FileSystemConnector(
    purview_client=purview_client,
    root_path=os.getenv("ROOT_PATH"),
    file_extensions=['.csv', '.xlsx', '.json', '.parquet'],
    recursive=True,
    collection_name=os.getenv("COLLECTION_NAME", "FileAssets")
)

# Scan and ingest
results = connector.scan_and_ingest()
print(f"Scanned {results['entities_extracted']} files")
print(f"Created {results['entities_created']} assets in Purview")
```

### Azure Blob Storage Example

```python
from purview_connector_sdk import PurviewClient, FileSystemConnector
from azure.storage.blob import BlobServiceClient

# Initialize Blob Storage client
blob_service = BlobServiceClient.from_connection_string(
    os.getenv("AZURE_STORAGE_CONNECTION_STRING")
)

# List blobs
container = blob_service.get_container_client("my-container")
blobs = list(container.list_blobs())

# Create metadata for Purview
file_metadata = {
    "root_path": f"wasbs://my-container@{storage_account}.blob.core.windows.net",
    "files": [
        {
            "name": blob.name,
            "path": f"{container.url}/{blob.name}",
            "size": blob.size,
            "extension": os.path.splitext(blob.name)[1],
            "modified": blob.last_modified.timestamp()
        }
        for blob in blobs
    ],
    "directories": []
}

# Transform and ingest
purview_client = PurviewClient.from_environment()
connector = FileSystemConnector(
    purview_client=purview_client,
    root_path=file_metadata["root_path"]
)

entities = connector.transform_to_atlas(file_metadata)
result = connector.ingest_to_purview(entities)
```

### Network Share via Gateway

For on-premises network shares:

```python
# In Fabric Notebook with Gateway
from purview_connector_sdk import PurviewClient, FileSystemConnector

purview_client = PurviewClient(
    account_name="your-purview",
    use_managed_identity=True
)

# Connect via gateway
connector = FileSystemConnector(
    purview_client=purview_client,
    root_path="\\\\server\\share\\data",
    file_extensions=['.csv', '.xlsx'],
    recursive=True,
    use_gateway=True,
    gateway_id="your-gateway-id",
    collection_name="NetworkShares"
)

results = connector.scan_and_ingest()
```

## Advanced Features

### File Content Parsing

Extract schema from CSV files:

```python
import pandas as pd
from purview_connector_sdk import Entity

def extract_csv_schema(file_path):
    """Extract column information from CSV file"""
    df = pd.read_csv(file_path, nrows=1000)  # Sample first 1000 rows
    
    columns = []
    for col in df.columns:
        columns.append({
            "name": col,
            "data_type": str(df[col].dtype),
            "nullable": df[col].isnull().any()
        })
    
    return columns

# Use in connector
class CSVConnector(FileSystemConnector):
    def extract_metadata(self):
        metadata = super().extract_metadata()
        
        # Add schema info for CSV files
        for file in metadata['files']:
            if file['extension'] == '.csv':
                try:
                    file['columns'] = extract_csv_schema(file['path'])
                except Exception as e:
                    logger.warning(f"Failed to parse {file['name']}: {e}")
        
        return metadata
```

### File Classification

Automatically classify sensitive files:

```python
def classify_file(file_name, file_content):
    """Detect sensitive data in files"""
    classifications = []
    
    # Email detection
    if '@' in file_content:
        classifications.append("EmailAddress")
    
    # Credit card pattern
    import re
    if re.search(r'\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}', file_content):
        classifications.append("CreditCard")
    
    # SSN pattern
    if re.search(r'\d{3}-\d{2}-\d{4}', file_content):
        classifications.append("SSN")
    
    return classifications

# Add classifications to entities
entity["classifications"] = classify_file(file_name, content)
```

### Lineage Tracking

Track file transformations:

```python
def create_lineage(source_file, target_file, process_name):
    """Create lineage relationship between files"""
    
    # Source file entity
    source_entity = {
        "typeName": "DataSet",
        "attributes": {
            "qualifiedName": f"file://{source_file}",
            "name": os.path.basename(source_file)
        }
    }
    
    # Target file entity
    target_entity = {
        "typeName": "DataSet",
        "attributes": {
            "qualifiedName": f"file://{target_file}",
            "name": os.path.basename(target_file)
        }
    }
    
    # Process entity (transformation)
    process_entity = {
        "typeName": "Process",
        "attributes": {
            "qualifiedName": f"process://{process_name}",
            "name": process_name,
            "inputs": [source_entity],
            "outputs": [target_entity]
        }
    }
    
    return [source_entity, target_entity, process_entity]
```

## Running the Example

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the example
python file_connector_example.py

# Output:
# Starting File System Connector Example
# Scanning directory: /data/files
# Found 125 files, 15 directories
# Transforming to Atlas format...
# Ingesting to Purview...
# ✓ Created 140 assets in Purview
```

## Supported File Types

| Type | Extension | Metadata Extracted |
|------|-----------|-------------------|
| CSV | .csv | Columns, data types, row count |
| Excel | .xlsx, .xls | Sheets, columns, data types |
| JSON | .json | Schema structure |
| Parquet | .parquet | Schema, partitions |
| Text | .txt | Size, encoding |
| PDF | .pdf | Pages, size |
| Images | .jpg, .png | Dimensions, size |

## Performance Tips

### Large Directories

For directories with thousands of files:

```python
# Use pagination
def scan_large_directory(root_path, batch_size=1000):
    files = list(Path(root_path).rglob("*"))
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i + batch_size]
        
        # Process batch
        metadata = create_metadata(batch)
        entities = transform_to_atlas(metadata)
        ingest_to_purview(entities)
        
        print(f"Processed batch {i//batch_size + 1}")
```

### Incremental Scanning

Only scan modified files:

```python
import json
from datetime import datetime

# Load last scan time
try:
    with open("last_scan.json", "r") as f:
        last_scan = json.load(f)
        last_scan_time = datetime.fromisoformat(last_scan["timestamp"])
except:
    last_scan_time = datetime(1970, 1, 1)

# Filter files modified since last scan
recent_files = [
    f for f in all_files
    if datetime.fromtimestamp(f.stat().st_mtime) > last_scan_time
]

# Save current scan time
with open("last_scan.json", "w") as f:
    json.dump({"timestamp": datetime.now().isoformat()}, f)
```

## Troubleshooting

### Permission Errors

**Error**: "Permission denied"

```bash
# Check file permissions
ls -la /path/to/files

# Grant read access
chmod -R +r /path/to/files
```

### Network Path Issues

**Error**: "Path not found: \\\\server\\share"

```python
# Windows - ensure path is properly formatted
import os
path = r"\\server\share\folder"  # Use raw string

# Or use forward slashes
path = "//server/share/folder"
```

### Large Files

For very large files (>1GB):

```python
# Stream file content instead of loading entirely
def stream_large_file(file_path):
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):  # Read 8KB at a time
            process_chunk(chunk)
```

## Next Steps

- [Advanced File Parsing](./advanced_parsing.md)
- [Schema Detection](../../docs/schema-detection.md)
- [Classification Rules](../../docs/classification.md)
- [Lineage Tracking](../etl-lineage/README.md)

## Resources

- [PyApacheAtlas Documentation](https://wjohnson.github.io/pyapacheatlas-docs/)
- [Azure Storage Python SDK](https://docs.microsoft.com/python/api/azure-storage-blob/)
- [Pandas Documentation](https://pandas.pydata.org/)

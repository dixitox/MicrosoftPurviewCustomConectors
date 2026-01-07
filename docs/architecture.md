# Architecture Guide

This document provides a detailed explanation of the Microsoft Purview Custom Connector Solution Accelerator architecture.

## Table of Contents
- [Overview](#overview)
- [Architecture Patterns](#architecture-patterns)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Deployment Models](#deployment-models)

## Overview

The solution accelerator follows a modular, extensible architecture that separates concerns:

1. **Data Source Layer** - Where your data resides
2. **Connectivity Layer** - Gateway and connection management
3. **Processing Layer** - Metadata extraction and transformation
4. **Orchestration Layer** - Workflow and scheduling
5. **Governance Layer** - Purview catalog and data map

## Architecture Patterns

### Pattern 1: Cloud-to-Cloud

```
┌─────────────────┐
│  Azure SQL DB   │
│  Blob Storage   │
│  Cosmos DB      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fabric Notebook │
│ (Metadata Scan) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Purview      │
│   Data Map      │
└─────────────────┘
```

**Use Case**: Azure-native data sources

**Benefits**:
- Managed Identity authentication
- No gateway required
- Native Azure integration
- High performance

### Pattern 2: On-Premises via Gateway

```
┌──────────────────────┐
│   On-Prem Network    │
│  ┌────────────────┐  │
│  │ SQL Server     │  │
│  │ File Share     │  │
│  │ Oracle DB      │  │
│  └───────┬────────┘  │
│          │           │
│  ┌───────▼────────┐  │
│  │  Data Gateway  │  │
│  └───────┬────────┘  │
└──────────┼───────────┘
           │ HTTPS
┌──────────▼───────────┐
│  Microsoft Fabric    │
│  ┌────────────────┐  │
│  │    Notebook    │  │
│  └───────┬────────┘  │
│  ┌───────▼────────┐  │
│  │    Pipeline    │  │
│  └───────┬────────┘  │
└──────────┼───────────┘
           │
┌──────────▼───────────┐
│      Purview         │
└──────────────────────┘
```

**Use Case**: On-premises databases and file systems

**Benefits**:
- Secure connectivity without opening firewalls
- Supports legacy systems
- Centralized management
- Scheduled scanning

### Pattern 3: Hybrid Multi-Cloud

```
┌─────────┐  ┌─────────┐  ┌─────────┐
│  Azure  │  │   AWS   │  │   GCP   │
│ Sources │  │ Sources │  │ Sources │
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
     └────────────┼────────────┘
                  │
         ┌────────▼────────┐
         │ Fabric Lakehouse │
         │  (Metadata Hub)  │
         └────────┬─────────┘
                  │
         ┌────────▼────────┐
         │  Purview        │
         │  (Unified Gov)  │
         └─────────────────┘
```

**Use Case**: Multi-cloud environments

**Benefits**:
- Unified governance
- Cross-cloud lineage
- Centralized discovery
- Consistent policies

## Component Details

### 1. Purview Connector SDK

**Purpose**: Python library for building connectors

**Key Classes**:
- `PurviewClient` - Authentication and API interaction
- `BaseConnector` - Abstract base for all connectors
- `DatabaseConnector` - SQL database sources
- `FileSystemConnector` - File system sources
- `APIConnector` - REST API sources

**Responsibilities**:
- Authentication management
- Metadata extraction
- Atlas format transformation
- Entity ingestion
- Error handling and retry logic

### 2. Microsoft Fabric (Recommended Platform)

**Components**:

#### Fabric Notebooks
- **Purpose**: Metadata extraction and transformation
- **Language**: Python/PySpark
- **Key Libraries**: 
  - pyapacheatlas
  - pandas
  - pyspark
- **Execution**: Serverless Spark clusters

#### Fabric Pipelines
- **Purpose**: Orchestration and scheduling
- **Activities**:
  - Notebook execution
  - Data movement
  - Conditional logic
  - Error handling
- **Triggers**:
  - Schedule (cron-like)
  - Tumbling window
  - Event-based

#### Lakehouse
- **Purpose**: Staging area for metadata
- **Storage**:
  - `/staging` - Raw metadata
  - `/processed` - Atlas JSON
  - `/logs` - Execution logs
  - `/archive` - Historical data

### 3. On-Premises Data Gateway

**Architecture**:
```
On-Prem Network              Azure
┌─────────────────────┐    ┌──────────────────┐
│   Data Gateway      │    │  Gateway Service │
│   - Agent Service   │◄──►│  (Azure Relay)   │
│   - Local Proxy     │    └──────────────────┘
└─────────────────────┘              ▲
         ▲                           │
         │                           │
    ┌────┴─────┐              ┌─────┴──────┐
    │ SQL DB   │              │   Fabric   │
    │ Files    │              │  Notebook  │
    └──────────┘              └────────────┘
```

**Features**:
- Secure outbound-only connection (port 443)
- No VPN or firewall changes needed
- Supports multiple data sources
- High availability with clustering
- Monitoring and diagnostics

### 4. Microsoft Purview

**Components Used**:

#### Data Map
- **Purpose**: Metadata repository
- **Technology**: Apache Atlas
- **Storage**: Entities, types, relationships, classifications

#### Collections
- **Purpose**: Organization and access control
- **Hierarchy**: Supports nested structure
- **Permissions**: RBAC at collection level

#### Data Catalog
- **Purpose**: Search and discovery
- **Features**:
  - Full-text search
  - Faceted filtering
  - Asset preview
  - User annotations

## Data Flow

### Ingestion Flow

```
1. Trigger Pipeline
   │
   ├─→ Schedule (cron)
   ├─→ Manual execution
   └─→ Event (new data)
   
2. Extract Metadata
   │
   ├─→ Connect to source
   ├─→ Query system tables
   ├─→ Scan files/folders
   └─→ Call APIs
   
3. Transform to Atlas
   │
   ├─→ Map to entity types
   ├─→ Generate qualified names
   ├─→ Create relationships
   └─→ Add classifications
   
4. Validate Entities
   │
   ├─→ Check required fields
   ├─→ Validate format
   └─→ Ensure consistency
   
5. Stage to Lakehouse
   │
   ├─→ Write JSON files
   ├─→ Partition by date
   └─→ Log metadata
   
6. Ingest to Purview
   │
   ├─→ Bulk create entities
   ├─→ Create relationships
   ├─→ Apply classifications
   └─→ Update lineage
   
7. Post-Processing
   │
   ├─→ Log results
   ├─→ Send notifications
   └─→ Update checkpoint
```

### Entity Relationship Model

```
┌──────────────┐
│   Database   │
└──────┬───────┘
       │ contains
       ▼
┌──────────────┐
│    Schema    │
└──────┬───────┘
       │ contains
       ▼
┌──────────────┐
│    Table     │◄──── lineage ──────┐
└──────┬───────┘                    │
       │ contains                   │
       ▼                            │
┌──────────────┐              ┌─────┴──────┐
│    Column    │              │  Process   │
└──────────────┘              │ (ETL Job)  │
                              └────────────┘
```

## Deployment Models

### Model 1: Single Workspace

```
Fabric Workspace: "Purview-Connectors"
├── Lakehouse: metadata_lake
├── Notebook: extract_metadata
├── Notebook: transform_atlas
├── Notebook: ingest_purview
└── Pipeline: orchestration
```

**Best For**: Small to medium deployments, single team

### Model 2: Multi-Workspace

```
Fabric Workspace: "Data-Engineering"
├── Lakehouse: raw_metadata
└── Pipeline: data_extraction

Fabric Workspace: "Governance"
├── Lakehouse: purview_metadata
├── Notebook: atlas_transformer
├── Notebook: purview_ingestion
└── Pipeline: governance_workflow
```

**Best For**: Large organizations, separation of concerns

### Model 3: Hub and Spoke

```
Hub Workspace: "Purview-Hub"
├── Lakehouse: central_metadata
└── Pipeline: aggregation

Spoke Workspace: "Finance-Data"
├── Pipeline: extract_finance_db

Spoke Workspace: "Sales-Data"
├── Pipeline: extract_sales_db

Spoke Workspace: "HR-Data"
├── Pipeline: extract_hr_db
```

**Best For**: Enterprise scale, domain-driven architecture

## Security Architecture

### Authentication Flow

```
Service Principal / Managed Identity
           │
           ▼
    Azure AD Token
           │
           ├─→ Purview API (Data Curator)
           ├─→ Fabric API (Contributor)
           └─→ Data Sources (Reader)
```

### Network Security

```
On-Prem Network        DMZ              Azure
┌──────────────┐   ┌─────────┐    ┌──────────┐
│ Data Sources │──►│ Gateway │───►│ Fabric   │
└──────────────┘   └─────────┘    └────┬─────┘
                                        │
                                        ▼
                   Private Endpoint  ┌──────────┐
                   ◄────────────────►│ Purview  │
                                     └──────────┘
```

## Performance Considerations

### Scaling Strategies

1. **Parallel Processing**
   - Multiple notebooks running concurrently
   - Spark partitioning for large datasets
   - Batch entity creation (100-500 per batch)

2. **Incremental Scanning**
   - Track last scan timestamp
   - Only process changes
   - Use change data capture when available

3. **Caching**
   - Cache entity GUIDs
   - Reuse type definitions
   - Store reference data

### Optimization Tips

- Use Fabric Spark pools for large metadata sets
- Partition Lakehouse data by date/source
- Implement checkpointing for long-running scans
- Use Delta tables for ACID guarantees
- Compress staged JSON files

## Monitoring and Observability

### Metrics to Track

- Entities scanned per run
- Ingestion success rate
- Processing duration
- Error counts
- Gateway availability

### Logging Strategy

```python
# Application logs → Lakehouse
logger.info("Scan started", extra={
    "source": "sql_server",
    "timestamp": datetime.now(),
    "entities_count": 1000
})

# Azure Monitor → Alerts
# Log Analytics → Dashboards
# Application Insights → Distributed tracing
```

## Next Steps

- [Fabric Integration Guide](./fabric-integration.md)
- [Developer Guide](./developer-guide.md)
- [Best Practices](./best-practices.md)

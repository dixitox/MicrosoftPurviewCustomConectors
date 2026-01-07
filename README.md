# Microsoft Purview Custom Connector Solution Accelerator

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Azure](https://img.shields.io/badge/azure-Purview%20%7C%20Fabric-blue)

A comprehensive solution accelerator to help organizations rapidly develop custom connectors for Microsoft Purview, enabling metadata scanning and lineage tracking for data sources not natively supported by Purview.

## 🎯 Overview

Microsoft Purview is a unified data governance service that helps manage and govern on-premises, multi-cloud, and SaaS data. While Purview provides native connectors for many popular data sources, organizations often need to integrate custom or proprietary data sources. This Solution Accelerator provides:

- **Jump-start development** with patterns, reusable tooling, and step-by-step documentation
- **Extensibility** using the open Apache Atlas API
- **Microsoft Fabric integration** for compute and orchestration, especially for on-premises and complex data sources
- **Custom type management** for defining metadata schemas
- **Sample implementations** for databases, file systems, and ETL tools

## 🏗️ Architecture

This accelerator leverages **Microsoft Fabric** (recommended) for modern, cloud-native infrastructure:

```
┌─────────────────────────────────────────────────────────────────┐
│                     Data Sources                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ On-Prem  │  │  Custom  │  │   File   │  │   ETL    │        │
│  │ Database │  │   APIs   │  │ Systems  │  │  Tools   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              On-Premises Data Gateway (Optional)                 │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Microsoft Fabric                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Fabric Notebooks (Python/PySpark)                      │   │
│  │  • Metadata extraction                                   │   │
│  │  • Transformation to Atlas JSON                         │   │
│  │  • Custom type handling                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Fabric Data Pipelines                                   │   │
│  │  • Orchestration & scheduling                           │   │
│  │  • Error handling & logging                             │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Microsoft Purview                              │
│  • Data Catalog                                                  │
│  • Data Map                                                      │
│  • Lineage Tracking                                             │
│  • Classification & Labeling                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Why Microsoft Fabric?

For on-premises and complex data sources, **Microsoft Fabric** is the recommended platform:

- **Unified analytics platform** combining data engineering, science, and warehousing
- **On-premises Data Gateway** for secure connectivity to on-prem sources
- **Serverless compute** with Fabric Spark pools
- **Native Purview integration** for seamless governance
- **Pipeline orchestration** with built-in monitoring and logging
- **Future-proof** as Microsoft's strategic analytics platform

## 🚀 Getting Started

### Prerequisites

- **Azure Subscription** with appropriate permissions
- **Microsoft Purview** account
- **Microsoft Fabric** workspace (recommended) OR Azure Synapse workspace
- **Python 3.8+** for local development
- **Service Principal** or **Managed Identity** for authentication
- **On-Premises Data Gateway** (if connecting to on-prem sources)

### Quick Start

1. **Clone this repository**
   ```bash
   git clone https://github.com/dixitox/MicrosoftPurviewCustomConectors.git
   cd MicrosoftPurviewCustomConectors
   ```

2. **Deploy infrastructure**
   ```bash
   cd deployment
   # Follow deployment guide for your chosen platform (Fabric or Synapse)
   ./deploy-fabric.sh  # For Microsoft Fabric (recommended)
   ```

3. **Configure authentication**
   - Create a Service Principal in Azure AD
   - Grant necessary permissions to Purview and data sources
   - See [Authentication Guide](./docs/authentication.md)

4. **Run example connector**
   ```bash
   cd examples/database-connector
   # Follow the example-specific README
   ```

## 📁 Repository Structure

```
.
├── docs/                           # Comprehensive documentation
│   ├── architecture.md            # Architecture deep dive
│   ├── authentication.md          # Authentication setup
│   ├── fabric-integration.md      # Microsoft Fabric guide
│   ├── custom-types.md           # Custom type management
│   └── best-practices.md         # Best practices & guidelines
│
├── deployment/                    # Infrastructure deployment
│   ├── fabric/                   # Microsoft Fabric templates
│   ├── synapse/                  # Azure Synapse templates (legacy)
│   ├── bicep/                    # Azure Bicep templates
│   └── terraform/                # Terraform templates
│
├── src/                          # Core framework and utilities
│   ├── purview_connector_sdk/   # Python SDK for connectors
│   ├── atlas_utils/             # Apache Atlas API utilities
│   ├── fabric_utils/            # Microsoft Fabric helpers
│   └── common/                  # Shared utilities
│
├── examples/                     # Sample connector implementations
│   ├── database-connector/      # Database source example
│   ├── file-connector/          # File system example
│   ├── api-connector/           # REST API example
│   └── etl-lineage/            # ETL tool lineage example
│
├── notebooks/                    # Fabric/Synapse notebooks
│   ├── fabric/                  # Microsoft Fabric notebooks
│   └── synapse/                 # Synapse notebooks (legacy)
│
├── pipelines/                    # Pipeline definitions
│   ├── fabric/                  # Fabric pipeline JSON
│   └── synapse/                 # Synapse pipeline JSON
│
├── tests/                        # Unit and integration tests
│   ├── unit/
│   └── integration/
│
└── tools/                        # Development tools
    ├── custom-types-tool/       # Custom type definition tool
    └── testing-utilities/       # Testing helpers
```

## 🔧 Core Features

### 1. Connector Framework
- **Python SDK** for building custom connectors
- **Apache Atlas API** integration
- **Metadata extraction templates**
- **Error handling and retry logic**
- **Logging and monitoring**

### 2. Microsoft Fabric Integration
- **Fabric Notebooks** for data processing
- **Fabric Pipelines** for orchestration
- **On-Premises Gateway** support
- **Lakehouse** integration for metadata storage
- **Fabric authentication** patterns

### 3. Custom Type Management
- **Type definition** utilities
- **Schema validation**
- **Relationship mapping**
- **Entity templates**

### 4. Sample Connectors
- **Database Connector**: SQL Server, PostgreSQL, MySQL
- **File System Connector**: Local files, network shares
- **API Connector**: REST API integration
- **ETL Lineage**: SSIS, ADF, custom ETL tools

## 📚 Documentation

- [Architecture Guide](./docs/architecture.md) - Detailed architecture explanation
- [Getting Started Guide](./docs/getting-started.md) - Step-by-step setup
- [Microsoft Fabric Integration](./docs/fabric-integration.md) - Fabric-specific guidance
- [Authentication Setup](./docs/authentication.md) - Security configuration
- [Custom Types Guide](./docs/custom-types.md) - Define custom metadata
- [Developer Guide](./docs/developer-guide.md) - Build your own connector
- [Best Practices](./docs/best-practices.md) - Production recommendations
- [Troubleshooting](./docs/troubleshooting.md) - Common issues and solutions

## 💡 Examples

### Database Connector
```python
from purview_connector_sdk import DatabaseConnector

connector = DatabaseConnector(
    source_type="sql_server",
    connection_string="Server=myserver;Database=mydb",
    purview_account="my-purview-account"
)

# Scan and ingest metadata
connector.scan_and_ingest()
```

See [Database Connector Example](./examples/database-connector/README.md) for full details.

### File System Connector
```python
from purview_connector_sdk import FileSystemConnector

connector = FileSystemConnector(
    root_path="/data/files",
    purview_account="my-purview-account"
)

connector.scan_and_ingest()
```

See [File System Connector Example](./examples/file-connector/README.md) for full details.

## 🔒 Security Best Practices

- Use **Managed Identity** when possible (for Azure resources)
- Use **Service Principal** with least-privilege permissions
- Store credentials in **Azure Key Vault**
- Enable **audit logging** for all operations
- Implement **data classification** during ingestion
- Follow **network security** guidelines for on-prem connectivity

See [Security Guide](./docs/security.md) for comprehensive security recommendations.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](./CONTRIBUTING.md) for details.

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

This solution builds upon:
- [Microsoft Purview Custom Connector Solution Accelerator](https://github.com/microsoft/Purview-Custom-Connector-Solution-Accelerator) - Original solution using Azure Synapse
- [PurviewCustomScanner](https://github.com/israeloros/PurviewCustomScanner) - Community solution for SharePoint and file systems
- [PyApacheAtlas](https://github.com/wjohnson/pyapacheatlas) - Python library for Apache Atlas

## 📞 Support

- **Issues**: Please use [GitHub Issues](https://github.com/dixitox/MicrosoftPurviewCustomConectors/issues) for bug reports and feature requests
- **Questions**: Use [GitHub Discussions](https://github.com/dixitox/MicrosoftPurviewCustomConectors/discussions) for general questions
- **Documentation**: See the [docs](./docs) folder for detailed guides

## 🗺️ Roadmap

- [x] Core framework and SDK
- [x] Microsoft Fabric integration
- [x] Database connector example
- [ ] File system connector example
- [ ] ETL lineage example (SSIS, ADF)
- [ ] API connector example
- [ ] Kafka endpoint integration for high-volume scenarios
- [ ] Advanced classification with AI
- [ ] Multi-region deployment templates

## ⚡ What's New

### Focus on Microsoft Fabric
This updated solution accelerator emphasizes **Microsoft Fabric** as the recommended platform for:
- **On-premises connectivity** via Data Gateway
- **Modern analytics** with unified workspace
- **Future-proof architecture** aligned with Microsoft's strategic direction
- **Simplified deployment** with serverless compute

### Key Improvements over Original Solution
- ✅ Microsoft Fabric support (vs. Synapse-only)
- ✅ Modern Python SDK design
- ✅ Comprehensive documentation
- ✅ More connector examples
- ✅ Better error handling
- ✅ Testing utilities
- ✅ CI/CD integration examples

---

**Note**: This is a Solution Accelerator, not a production-ready product. Customization will be required for your specific use cases and data sources.
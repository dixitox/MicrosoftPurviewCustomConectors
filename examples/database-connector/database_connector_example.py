"""
Database Connector Example

This script demonstrates how to use the DatabaseConnector to scan
a SQL database and ingest metadata into Microsoft Purview.
"""

import os
import logging
from dotenv import load_dotenv
from purview_connector_sdk import PurviewClient, DatabaseConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the database connector example."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    logger.info("Starting Database Connector Example")
    
    # Step 1: Initialize Purview Client
    logger.info("Initializing Purview client...")
    try:
        purview_client = PurviewClient.from_environment()
        logger.info(f"Connected to Purview: {purview_client.endpoint}")
    except Exception as e:
        logger.error(f"Failed to initialize Purview client: {e}")
        return
    
    # Step 2: Configure database connection
    db_type = os.getenv("DB_TYPE", "sql_server")
    db_server = os.getenv("DB_SERVER")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    
    # Build connection string based on database type
    if db_type == "sql_server":
        connection_string = (
            f"Driver={{ODBC Driver 17 for SQL Server}};"
            f"Server={db_server};"
            f"Database={db_name};"
            f"UID={db_user};"
            f"PWD={db_password}"
        )
    elif db_type == "postgresql":
        connection_string = (
            f"postgresql://{db_user}:{db_password}@{db_server}/{db_name}"
        )
    elif db_type == "mysql":
        connection_string = (
            f"mysql+pymysql://{db_user}:{db_password}@{db_server}/{db_name}"
        )
    else:
        logger.error(f"Unsupported database type: {db_type}")
        return
    
    # Step 3: Create database connector
    logger.info(f"Creating connector for {db_type} database...")
    connector = DatabaseConnector(
        purview_client=purview_client,
        source_type=db_type,
        connection_string=connection_string,
        collection_name=os.getenv("COLLECTION_NAME", "DatabaseAssets"),
        qualified_name_prefix=f"{db_type}://{db_server}/{db_name}"
    )
    
    # Step 4: Scan and ingest
    logger.info("Starting scan and ingest process...")
    try:
        results = connector.scan_and_ingest()
        
        logger.info("=" * 60)
        logger.info("Scan and Ingest Results:")
        logger.info(f"  Status: {results['status']}")
        logger.info(f"  Entities Extracted: {results['entities_extracted']}")
        logger.info(f"  Entities Created: {results['entities_created']}")
        logger.info("=" * 60)
        
        # Display some metadata
        metadata = results.get('metadata', {})
        logger.info(f"Database: {metadata.get('database_name')}")
        schemas = metadata.get('schemas', [])
        logger.info(f"Schemas: {len(schemas)}")
        
        for schema in schemas:
            logger.info(f"  Schema: {schema['name']}")
            tables = schema.get('tables', [])
            logger.info(f"    Tables: {len(tables)}")
            for table in tables[:5]:  # Show first 5 tables
                logger.info(f"      - {table['name']} ({len(table.get('columns', []))} columns)")
        
        logger.info("Database connector example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during scan and ingest: {e}", exc_info=True)
        return


if __name__ == "__main__":
    main()

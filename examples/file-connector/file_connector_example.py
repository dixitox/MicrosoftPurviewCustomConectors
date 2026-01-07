"""
File System Connector Example

This script demonstrates how to use the FileSystemConnector to scan
a file system and ingest metadata into Microsoft Purview.
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from purview_connector_sdk import PurviewClient, FileSystemConnector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main function to run the file system connector example."""
    
    # Load environment variables
    load_dotenv()
    
    logger.info("Starting File System Connector Example")
    
    # Step 1: Initialize Purview Client
    logger.info("Initializing Purview client...")
    try:
        purview_client = PurviewClient.from_environment()
        logger.info(f"Connected to Purview: {purview_client.endpoint}")
    except Exception as e:
        logger.error(f"Failed to initialize Purview client: {e}")
        return
    
    # Step 2: Get file system configuration
    root_path = os.getenv("ROOT_PATH", "./sample_data")
    recursive = os.getenv("RECURSIVE", "true").lower() == "true"
    extensions = os.getenv("FILE_EXTENSIONS", "").split(",")
    collection_name = os.getenv("COLLECTION_NAME", "FileAssets")
    
    # Clean up extensions list
    file_extensions = [ext.strip() for ext in extensions if ext.strip()]
    
    logger.info(f"Scanning directory: {root_path}")
    logger.info(f"Recursive: {recursive}")
    logger.info(f"File extensions filter: {file_extensions or 'All'}")
    
    # Step 3: Create file system connector
    connector = FileSystemConnector(
        purview_client=purview_client,
        root_path=root_path,
        file_extensions=file_extensions if file_extensions else None,
        recursive=recursive,
        collection_name=collection_name
    )
    
    # Step 4: Extract metadata
    logger.info("Extracting file metadata...")
    try:
        metadata = connector.extract_metadata()
        
        file_count = len(metadata.get('files', []))
        dir_count = len(metadata.get('directories', []))
        
        logger.info(f"Found {file_count} files and {dir_count} directories")
        
        # Display file summary
        if file_count > 0:
            logger.info("\nFile Summary:")
            
            # Group by extension
            from collections import defaultdict
            by_extension = defaultdict(int)
            total_size = 0
            
            for file in metadata['files']:
                ext = file.get('extension', 'no extension')
                by_extension[ext] += 1
                total_size += file.get('size', 0)
            
            for ext, count in sorted(by_extension.items()):
                logger.info(f"  {ext}: {count} files")
            
            # Convert size to human readable
            size_mb = total_size / (1024 * 1024)
            logger.info(f"  Total size: {size_mb:.2f} MB")
            
            # Show sample files
            logger.info("\nSample Files (first 10):")
            for file in metadata['files'][:10]:
                size_kb = file['size'] / 1024
                logger.info(f"  - {file['name']} ({size_kb:.2f} KB)")
        
    except Exception as e:
        logger.error(f"Error during metadata extraction: {e}", exc_info=True)
        return
    
    # Step 5: Transform to Atlas format
    logger.info("\nTransforming to Atlas format...")
    try:
        entities = connector.transform_to_atlas(metadata)
        logger.info(f"Created {len(entities)} entities")
    except Exception as e:
        logger.error(f"Error during transformation: {e}", exc_info=True)
        return
    
    # Step 6: Ingest to Purview
    logger.info("\nIngesting to Purview...")
    try:
        result = connector.ingest_to_purview(entities)
        
        logger.info("=" * 60)
        logger.info("Ingestion Results:")
        logger.info(f"  Status: {result.get('status', 'unknown')}")
        logger.info(f"  Entities Created: {result.get('entities_created', 0)}")
        logger.info("=" * 60)
        
        logger.info("\n✓ File system connector example completed successfully!")
        logger.info(f"Check Purview collection '{collection_name}' to view the assets")
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}", exc_info=True)
        return


def create_sample_data():
    """Create sample data for testing"""
    logger.info("Creating sample data...")
    
    sample_dir = Path("./sample_data")
    sample_dir.mkdir(exist_ok=True)
    
    # Create some sample files
    (sample_dir / "users.csv").write_text(
        "id,name,email\n"
        "1,John Doe,john@example.com\n"
        "2,Jane Smith,jane@example.com\n"
    )
    
    (sample_dir / "readme.txt").write_text(
        "Sample data directory for testing file system connector"
    )
    
    (sample_dir / "config.json").write_text(
        '{"setting1": "value1", "setting2": "value2"}'
    )
    
    # Create subdirectory
    sub_dir = sample_dir / "reports"
    sub_dir.mkdir(exist_ok=True)
    
    (sub_dir / "monthly_report.txt").write_text(
        "Monthly Report - January 2024"
    )
    
    logger.info(f"Sample data created in {sample_dir}")


if __name__ == "__main__":
    # Uncomment to create sample data
    # create_sample_data()
    
    main()

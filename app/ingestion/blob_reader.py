'''
This module provides functionality to download all blobs from a specified Azure Blob Storage container.
'''
import os
from azure.storage.blob import BlobServiceClient
from config.azure_config import AZURE_STORAGE_CONNECTION_STRING

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('blob_reader')

def download_blobs(container_name: str, download_folder: str):
    '''
    Download all blobs from a specified Azure Blob Storage container to a local folder.
    Args:
        container_name (str): The name of the Azure Blob Storage container.
        download_folder (str): The local folder where the blobs will be downloaded.
    Raises:
        ValueError: If the Azure Storage connection string is not set or if the container does not exist.
    '''
    # Ensure the download folder exists and if not, create it
    os.makedirs(download_folder, exist_ok=True)

    # Create a BlobServiceClient using the connection string
    if not AZURE_STORAGE_CONNECTION_STRING:
        logger.error("Azure Storage connection string is not set in the environment variables.")
        raise ValueError("Azure Storage connection string is not set in the environment variables.")
    blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

    # Get the container client
    container_client = blob_service_client.get_container_client(container_name)

    # Check if the container exists
    if not container_client.exists():
        logger.error(f"Container '{container_name}' does not exist in blob storage.")
        raise ValueError(f"Container '{container_name}' does not exist in blob storage.")
    
    # List and download all blobs in the container to data folder
    for blob in container_client.list_blobs():
        blob_path = os.path.join(download_folder, blob.name)
        with open(blob_path, "wb") as f:
            blob_data = container_client.download_blob(blob.name)
            f.write(blob_data.readall())

    logger.info(f"✅ All files downloaded to: {download_folder}")
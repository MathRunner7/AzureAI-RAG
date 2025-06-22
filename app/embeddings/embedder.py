'''
Module for generating embeddings using either a local model or Azure OpenAI service.
This module provides functions to get embeddings for text chunks using:
- A local SentenceTransformer model.
- Azure OpenAI's embedding service.

Stored embeddings can be saved in either:
- Azure AI Search for cloud-based search capabilities.
- A local FAISS index for efficient similarity search.
This module also handles logging and configuration for both local and Azure services.
'''

import os
from typing import List

# For Azure
from  openai import AzureOpenAI
# For local embedding
from sentence_transformers import SentenceTransformer

# Azure Search
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# FAISS
import faiss
import pickle
import numpy as np

# Import configuration settings for Azure OpenAI and Search
from config.azure_config import (LOCAL_EMBEDDING_MODEL_NAME,LOCAL_VECTOR_DB_DIRECTORY,
        AZURE_OPENAI_EMBEDDING_API_KEY, AZURE_OPENAI_EMBEDDING_ENDPOINT, AZURE_OPENAI_EMBEDDING_DEPLOYMENT, AZURE_OPENAI_EMBEDDING_VERSION,
        AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_ADMIN_KEY, AZURE_SEARCH_INDEX_NAME)

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('embedder')

def get_embedding_local(text: str) -> List[float]:
    '''Generate embedding for a given text using a local SentenceTransformer model.
    Args:
        text (str): The input text to be embedded.
    Returns:
        List[float]: The embedding vector as a list of floats.
    '''
    # Load local model once (on module load)
    local_model = SentenceTransformer(LOCAL_EMBEDDING_MODEL_NAME)
    # Check if the model is loaded
    if not local_model:
        logger.error("Local embedding model could not be loaded.")
        return []
    # Generate embedding using local model
    return local_model.encode(text).tolist()

def get_embedding_azure(text: str) -> List[float]:
    '''Generate embedding for a given text using Azure OpenAI service.
    Args:
        text (str): The input text to be embedded.
    Returns:
        List[float]: The embedding vector as a list of floats.
    '''
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_EMBEDDING_API_KEY,
        api_version=AZURE_OPENAI_EMBEDDING_VERSION,
        azure_endpoint=AZURE_OPENAI_EMBEDDING_ENDPOINT
    )
    try:
        # Generate embedding using Azure OpenAI
        response = client.embeddings.create(
            input=text,
            model=AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Azure embedding failed: {e}")
        return []

def get_embeddings(chunks: List[str], use_azure: bool = False) -> List[List[float]]:
    '''Generate embeddings for a list of text chunks.
    Args:
        chunks (List[str]): List of text chunks to be embedded.
        use_azure (bool): Flag to determine whether to use Azure OpenAI for embeddings.
    Returns:
        List[List[float]]: List of embedding vectors for each chunk.
    '''
    embeddings = []
    # Determine which embedding function to use based on the flag
    for idx, chunk in enumerate(chunks):
        if use_azure:   # Use Azure OpenAI for embeddings if the flag is set
            emb = get_embedding_azure(chunk)
            logger.info(f" Azure Embedding [{idx+1}/{len(chunks)}] - Length: {len(emb)}")
        else:           # Use local SentenceTransformer model for embeddings
            emb = get_embedding_local(chunk)
            logger.info(f" Local Embedding [{idx+1}/{len(chunks)}] - Length: {len(emb)}")
        embeddings.append(emb)
    return embeddings

def store_in_azure_ai_search(chunks: List[str], embeddings: List[List[float]]):
    '''Store embeddings in Azure AI Search.
    Args:
        chunks (List[str]): List of text chunks.
        embeddings (List[List[float]]): List of embedding vectors.
    '''
    # Set up Azure Search client
    client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    )

    # Prepare documents for upload
    batch = []
    for i, (chunk, vector) in enumerate(zip(chunks, embeddings)):
        doc = {
            "id": f"doc-{i}",
            "content": chunk,
            "embedding": vector
        }
        batch.append(doc)

    try:
        # Upload documents to Azure AI Search
        result = client.upload_documents(documents=batch)
        logger.info(f"✅ Uploaded {len(result)} documents to Azure AI Search")
    except Exception as e:
        logger.error(f"❌ Azure Search upload failed: {e}")


def store_in_local_faiss(chunks: List[str], embeddings: List[List[float]]):
    '''Store embeddings in a local FAISS index.
    Args:
        chunks (List[str]): List of text chunks.
        embeddings (List[List[float]]): List of embedding vectors.
    '''
    # Ensure local_db directory exists
    dir = LOCAL_VECTOR_DB_DIRECTORY
    os.makedirs(dir, exist_ok=True)

    # Initialize FAISS index
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)

    # Add embeddings
    index.add(np.array(embeddings).astype('float32'))

    # Save FAISS index
    faiss.write_index(index, f"{dir}/faiss.index")

    # Save chunk text mapping
    with open(f"{dir}/id_to_chunk.pkl", "wb") as f:
        pickle.dump(chunks, f)

    logger.info(f"✅ Stored {len(embeddings)} embeddings in local FAISS index")

def store_embeddings(chunks: List[str], embeddings: List[List[float]], use_azure: bool = False):
    '''
    Store embeddings in either Azure AI Search or local FAISS index.
    Args:
        chunks (List[str]): List of text chunks.
        embeddings (List[List[float]]): List of embedding vectors.
        use_azure (bool): Flag to determine whether to use Azure AI Search for storage.
    '''
    if use_azure:
        store_in_azure_ai_search(chunks, embeddings)
    else:
        store_in_local_faiss(chunks, embeddings)
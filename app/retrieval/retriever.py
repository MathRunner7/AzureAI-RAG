'''
Module for retrieving top-k chunks from either Azure AI Search or a local FAISS index.
'''
import pickle
import numpy as np
from typing import List

# Azure Search
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

# FAISS
import faiss

# Import configuration settings for Azure OpenAI and Search
from config.azure_config import (AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_ADMIN_KEY, AZURE_SEARCH_INDEX_NAME, LOCAL_VECTOR_DB_DIRECTORY)

# Embedding
from app.embeddings.embedder import get_embeddings

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('retriever')

def search_chunks_azure(query_embedding: List[float], k: int) -> List[str]:
    '''
    Searches for top-k chunks in Azure AI Search using the provided query embedding.
    Args:
        query_embedding (List[float]): The embedding vector for the query.
        k (int): The number of top results to return.
    Returns:
        List[str]: A list of top-k chunks retrieved from Azure AI Search.
    '''
    try:
        # Set up Azure Search client
        client = SearchClient(
            endpoint=AZURE_SEARCH_ENDPOINT,
            index_name=AZURE_SEARCH_INDEX_NAME,
            credential=AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
        )
        
        # Convert query_embedding to a list if it's a numpy array
        results = client.search(
            search_text=None,
            vector_queries=[{'kind': 'vector', 'vector': query_embedding, 'fileds': 'embedding', 'k': k}],
            select=["content"],  # Assuming 'content' is the field containing the text chunks
        )

        return [doc['content'] for doc in results]

    except Exception as e:
        logger.error(f"Azure retrieval failed: {e}")
        return []

def search_chunks_local(query_embedding: List[float], k: int) -> List[str]:
    '''
    Searches for top-k chunks in a local FAISS index using the provided query embedding.
    Args:
        query_embedding (List[float]): The embedding vector for the query.
        k (int): The number of top results to return.
    Returns:
        List[str]: A list of top-k chunks retrieved from the local FAISS index.
    '''
    dir = LOCAL_VECTOR_DB_DIRECTORY
    try:
        index = faiss.read_index(f"{dir}/faiss.index")

        with open(f"{dir}/id_to_chunk.pkl", "rb") as f:
            chunks = pickle.load(f)

        query_vector = np.array([query_embedding]).astype('float32')
        _, indices = index.search(query_vector, k)

        return [chunks[i] for i in indices[0]]

    except Exception as e:
        logger.error(f"Local FAISS retrieval failed: {e}")
        return []

def get_top_k_chunks(query: str, k: int = 3, use_azure: bool = False) -> List[str]:
    '''
    Retrieves top-k similar chunks to the input query from either Azure AI Search or FAISS (local).
    Args:
        query (str): The input query for which to find similar chunks.
        k (int): The number of top results to return.
        use_azure (bool): Flag to determine whether to use Azure services or local model.
    Returns:
        List[str]: A list of top-k chunks similar to the input query.
    '''
    embedding = get_embeddings(chunks=[query], use_azure=use_azure)

    if use_azure:
        return search_chunks_azure(embedding, k)
    else:
        return search_chunks_local(embedding, k)
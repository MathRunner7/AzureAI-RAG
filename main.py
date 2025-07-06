'''
Main script to run the document ingestion and processing pipeline.
This script performs following operations.
1. Downloads documents from Azure Blob Storage
2. Extracts text from them
3. Processes the extracted text into chunks and save them 
4. Generates embeddings for the text chunks and Saves the chunks + embeddings for further use
5. Retrieves relevant chunks based on a user query and generates an answer using those chunks.
6. Generates an answer using the retrieved chunks and the user's query.
'''
from app.ingestion.blob_reader import download_blobs, generate_sas_url
from app.ingestion.text_extractor import process_all_documents, process_blob_files
from app.preprocessing.chunker import process_extracted_files
from app.embeddings.embedder import get_embeddings, store_embeddings
from app.retrieval.retriever import get_top_k_chunks
from app.generation.generator import generate_answer

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('mainlogger')

def main(query: str, use_azure: bool = False):
    '''Main function to execute the RAG pipeline.
    Args:
        query (str): The question to be answered.
        use_azure (bool): Flag to determine whether to use Azure services or local model.
    Returns:
        None'''
    try:
        # Download the blob file
        container = "documents"     # Your Azure Blob container name
        #logger.info("🔹 Step 1: Ingesting from Azure Blob")
        #download_blobs(container_name=container, download_folder="data/")
        logger.info("🔹 Step 1: Generate SAS urls for blobs")
        blob_urls = generate_sas_url(container_name=container, expiry_hours=1)

        #logger.info("🔹 Step 2: Extract content from all documents")
        #process_all_documents(input_folder="data/", output_folder="extracted/")
        logger.info("🔹 Step 2: Process documents from blob and extract text")
        process_blob_files(sas_urls=blob_urls, output_folder="extracted/")
        
        logger.info("🔹 Step 3: Cleaning and Chunking of extracted text data")
        chunks = process_extracted_files(input_folder="extracted/")


        logger.info("🔹 Step 4: Create embeddings and store them in Vector DB")
        embeddings = get_embeddings(chunks=chunks, use_azure=use_azure)
        store_embeddings(chunks=chunks, embeddings=embeddings, use_azure=use_azure)

        logger.info("🔹 Step 5: Retrieve relevant documents based on query")
        relevant_chunks = get_top_k_chunks(query=query, use_azure=use_azure)

        if not relevant_chunks:
            logger.warning("No relevant chunks found for the query.")
            return
        
        logger.info("🔹 Step 6: Generate answer using the retrieved chunks and the user's query")
        answer = generate_answer(query=query, context_chunks=relevant_chunks, use_azure=use_azure)

        # Print the final answer
        print("\n🔍 USER QUERY:\n" + query)
        print("\n🧠 FINAL RESPONSE:\n" + answer)
        logger.info("✅ RAG Pipeline executed successfully")

    except Exception as e:
        logger.exception(f"❌ Error in RAG pipeline: {e}")

if __name__ == "__main__":
    use_azure = True           # Set to True to use Azure services, False for local model
    # Example: replace with a real blob filename and user query
    query = "How to perform auto calibration? And what to do if any error occurred during calibration?"

    # use_azure=True enables Azure embedding & search; False = local mode
    main(query=query, use_azure=use_azure)
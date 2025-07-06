'''
Text extraction from documents using Azure Form Recognizer.
This module provides functionality to extract text from documents using Azure Form Recognizer.
'''

import os
from urllib.parse import urlparse
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config.azure_config import AZURE_FORM_RECOGNIZER_ENDPOINT, AZURE_FORM_RECOGNIZER_KEY

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('text_extractor')

def extract_text_from_file(file_path: str) -> str:
    '''
    Extract text from a document file using Azure Form Recognizer.
    Args:
        file_path (str): The path to the document file.
    Returns:
        str: The extracted text from the document.
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: If there is an error during text extraction.
    '''

    # Initialize the Document Analysis Client
    client = DocumentAnalysisClient(
        endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
        credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
    )

    # Open the file and analyze it 
    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-read", document=f)
        result = poller.result()

    # Extract text from the result, combining all lines into a single string and returning it
    full_text = "\n".join([line.content for page in result.pages for line in page.lines])
    return full_text

def process_all_documents(input_folder: str, output_folder: str) -> None:
    '''
    Process all documents in the input folder and save extracted text to the output folder.
    Args:
        input_folder (str): The folder containing the document files to process.
        output_folder (str): The folder where the extracted text files will be saved.
    Raises:
        Exception: If there is an error during processing of any file.
    Returns:
        None
    '''
    
    # Ensure the output folder exists and if not, create it
    os.makedirs(output_folder, exist_ok=True)

    # Process each file in the input folder
    for filename in os.listdir(input_folder):
        
        # Define the full path of the file
        file_path = os.path.join(input_folder, filename)
        logger.info(f"🔍 Processing: {filename} at {file_path}")
        try:
            # Extract text from the file and save it to the output_path
            text = extract_text_from_file(file_path)
            output_path = os.path.join(output_folder, filename + ".txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            
            # Delete the original file after processing
            os.remove(file_path)
            logger.info(f"✅ Successfully processed {filename} and saved to {output_path}")
        except Exception as e:
            logger.error(f"❌ Failed to process {filename}: {e}")

def flatten_table(table) -> str:
    """
    Flatten table to readable rows.
    Args:
        table (Table): The table object containing cells.
    Returns:
        str: A string representation of the table with rows and columns.
    """
    rows = []
    for row_idx in range(len(table.cells) // table.column_count):
        row = []
        for col_idx in range(table.column_count):
            cell = next(
                (c for c in table.cells if c.row_index == row_idx and c.column_index == col_idx), 
                None
            )
            row.append(cell.content.strip() if cell else "")
        rows.append(" | ".join(row))
    return "\n".join(rows)

def process_blob_files(sas_urls: list[str], output_folder: str) -> None:
    '''
    Process documents from Azure Blob Storage using SAS URLs and extract text.
    Args:
        sas_urls (list[str]): List of SAS URLs pointing to the documents in Azure Blob Storage.
        output_folder (str): The folder where the extracted text files will be saved.
    Raises:
        Exception: If there is an error during processing of any file.
    Returns:
        None
    '''
    try:
        # Initialize the Document Analysis Client
        client = DocumentAnalysisClient(
            endpoint=AZURE_FORM_RECOGNIZER_ENDPOINT,
            credential=AzureKeyCredential(AZURE_FORM_RECOGNIZER_KEY)
        )

        # Start the analysis process
        for sas_url in sas_urls:
            logger.info(f"🔍 Processing file from SAS URL: {sas_url}")
            # Analyze the document using the prebuilt-document model
            poller = client.begin_analyze_document_from_url(model_id="prebuilt-document", document_url=sas_url)
            result = poller.result()
            doc_text = []

            # Extract Paragraphs from the result
            if result.paragraphs:
                para = []
                for paragraph in result.paragraphs:
                    if paragraph.content:
                        para.append(paragraph.content.strip())
                doc_text.append("\n".join(para))
            
            # Extract key-value pairs from the result
            if result.key_value_pairs:
                kv = []
                for kvp in result.key_value_pairs:
                    if kvp.value and kvp.value.content.strip():
                        kv.append(f"{kvp.key.content.strip()}: {kvp.value.content.strip()}")
                doc_text.append("\n".join(kv))

            # Extract tables from the result
            if result.tables:
                tbl = []
                for table in result.tables:
                    flat_table = flatten_table(table)
                    if flat_table:
                        tbl.append(flat_table)
                doc_text.append("\n".join(tbl))
            # Combine all extracted text into a single string
            full_text = "\n\n".join(doc_text)
            
            # Save the extracted text to a file
            output_filename = urlparse(sas_url).path.split('/')[-1].split('.')[0] + ".txt"
            output_path = os.path.join("extracted", output_filename)
            os.makedirs("extracted", exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
                logger.info(f"✅ Successfully processed file: {output_filename} and saved to {output_path}")
    
    except Exception as e:
        logger.error(f"❌ Failed to process file: {e}")
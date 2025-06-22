'''
Text extraction from documents using Azure Form Recognizer.
This module provides functionality to extract text from documents using Azure Form Recognizer.
'''

import os
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


def process_all_documents(input_folder: str, output_folder: str):
    '''
    Process all documents in the input folder and save extracted text to the output folder.
    Args:
        input_folder (str): The folder containing the document files to process.
        output_folder (str): The folder where the extracted text files will be saved.
    Raises:
        Exception: If there is an error during processing of any file.
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

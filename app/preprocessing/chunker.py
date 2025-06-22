'''
Module for chunking text files into manageable pieces.
This module reads text files, cleans the text, and splits it into chunks based on a maximum token count.
'''

import os
import logging
from nltk.tokenize import sent_tokenize

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('chunker')

def chunk_text(text: str, max_tokens: int = 500, overlap: int = 100) -> list:
    '''Splits text into chunks of approximately max_tokens, allowing for overlap.
    Args:
        text (str): The text to be chunked.
        max_tokens (int): Maximum number of tokens per chunk.
        overlap (int): Number of tokens to overlap between chunks.
    Returns:
        list: A list of text chunks.
    '''
    
    # Tokenize the text into sentences
    sentences = sent_tokenize(text)

    # Initialize variables for chunking
    chunks = []
    current_chunk = []
    current_tokens = 0

    # Process each sentence and build chunks
    for sentence in sentences:
        # Count tokens in the current sentence
        token_count = len(sentence.split())

        # If adding this sentence leaves us under the max token limit, add it to the current chunk
        if current_tokens + token_count <= max_tokens:
            current_chunk.append(sentence)
            current_tokens += token_count
        # Else, finalize the current chunk and start a new one
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = current_chunk[-overlap:]  # overlap with last few sentences
            current_chunk.append(sentence)
            current_tokens = sum(len(s.split()) for s in current_chunk)

    # If there's any remaining text in the current chunk, add it to the list of chunks
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def clean_text(text: str) -> str:
    '''Cleans the input text by removing newlines and extra spaces.
    Args:
        text (str): The text to be cleaned.
    Returns:
        str: The cleaned text.
    '''
    cleaned = text.replace("\n", " ").strip()
    cleaned = " ".join(cleaned.split())  # remove extra spaces
    return cleaned


def process_extracted_files(input_folder: str) -> dict:
    '''Processes all text files in the input folder, cleaning and chunking them.
    Args:
        input_folder (str): Path to the folder containing text files.
    Returns:
        dict: A dictionary where keys are filenames and values are lists of text chunks.
    '''
    # Define the output variable in from of dictionary to hold all chunks
    all_chunks = {}

    # Process each text file in the input folder
    for filename in os.listdir(input_folder):
        # Only process .txt files
        if filename.endswith(".txt"):
            # Construct the full path to the file
            path = os.path.join(input_folder, filename)
            # Read the file content
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()

            # Clean and chunk the text
            cleaned = clean_text(text)
            chunks = chunk_text(cleaned)

            # Store the chunks in the dictionary
            all_chunks[filename] = chunks
            logger.info(f"✅ Chunked: {filename} → {len(chunks)} chunks")

            # Delete the original file after processing
            os.remove(path)
            logger.info(f"🗑️ Deleted: {filename}")

    return all_chunks
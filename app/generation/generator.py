'''
Module for generating answers using OpenAI's LLM (Azure or default).
This module provides a function to generate answers based on a query and context chunks.
'''

import os
from typing import List

# Azure OpenAI
from openai import AzureOpenAI

# Import configuration settings for Azure OpenAI and Search
from config.azure_config import (AZURE_OPENAI_CHAT_COMPLETION_API_KEY, AZURE_OPENAI_CHAT_COMPLETION_VERSION, AZURE_OPENAI_CHAT_COMPLETION_ENDPOINT, AZURE_OPENAI_CHAT_COMPLETION_DEPLOYMENT,
                                 LOCAL_LLM_MODEL_PATH)

# Hugging Face Transformers (for local LLM)
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Set up logging
from config.logging_config import setup_logging
logger = setup_logging('generator')

def generate_answer_azure(query: str, context_chunks: List[str]) -> str:
    '''
    Generate an answer using Azure OpenAI's LLM based on the provided query and context chunks.
    Args:
        query (str): The question to be answered.
        context_chunks (List[str]): List of context chunks to use for generating the answer.
    Returns:
        str: The generated answer.
    '''
    
    # Set up Azure OpenAI client
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_CHAT_COMPLETION_API_KEY,
        api_version=AZURE_OPENAI_CHAT_COMPLETION_VERSION,
        azure_endpoint=AZURE_OPENAI_CHAT_COMPLETION_ENDPOINT
    )
    deployment = AZURE_OPENAI_CHAT_COMPLETION_DEPLOYMENT

    # Construct the prompt for the LLM
    logger.info("Generating answer using Azure LLM")
    try:
        # Join context chunks into a single string
        context = "\n".join(context_chunks)

        # Construct the prompt with context and query
        prompt = f"""Use the following context to answer the question.
Context:
{context}

Question:
{query}
"""
        # Generate the answer using Azure OpenAI's chat completion
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": "You are an assistant that answers questions based on provided context."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Azure LLM generation failed: {e}")
        return "Sorry, failed to generate answer using Azure LLM."

def generate_answer_local(query: str, context_chunks: List[str]) -> str:
    '''
    Generate an answer using a local LLM based on the provided query and context chunks.
    Args:
        query (str): The question to be answered.
        context_chunks (List[str]): List of context chunks to use for generating the answer.
    Returns:
        str: The generated answer.
    '''
    logger.info("Generating answer using local LLM")
    try:
        # Load local model path from environment variable
        model_path = LOCAL_LLM_MODEL_PATH
        # Join context chunks into a single string
        context = "\n".join(context_chunks)
        # Construct the prompt with context and query
        prompt = f"""Use the following context to answer the question.
Context:
{context}

Question:
{query}
"""
        # Load the tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        # Create a text generation pipeline
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)
        # Generate the answer using the local model
        output = pipe(prompt, max_new_tokens=256, temperature=0.3)
        return output[0]['generated_text'].split("Answer:")[-1].strip()

    except Exception as e:
        logger.error(f"Local LLM generation failed: {e}")
        return "Sorry, failed to generate answer using local LLM."

def generate_answer(query: str, context_chunks: List[str], use_azure: bool = False) -> str:
    '''
    Generate an answer based on the provided query and context chunks using Azure OpenAI or a local model.
    Args:
        query (str): The question to be answered.
        context_chunks (List[str]): List of context chunks to use for generating the answer.
        use_azure (bool): Flag to determine whether to use Azure OpenAI or a local model.
    Returns:
        str: The generated answer.'''

    if use_azure:
        return generate_answer_azure(query, context_chunks)
    else:
        return generate_answer_local(query, context_chunks)
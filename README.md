# AzureAI-RAG
## RAG Application using Azure AI

### File Structure

```text
AzureAI-RAG/
├── config/                     # 🔧 Config files (keys, endpoints, constants)
│   └── azure_config.py
├── data/                       # 📁 Raw files downloaded from Azure Blob (Stored Temporarily)
├── extracted/                  # 📄 Cleaned text from documents (Stored Temporarily)
├── vectorstore/                # 📦 Stored embeddings (FAISS or similar)
├── models/                     # # 🤗 Hugging Face model storage folder
├── app/                        # 🧠 Core modules
│   ├── ingestion/              
│   │   ├── blob_reader.py      # Step 1: Ingest from Azure
│   │   └── text_extractor.py   # Step 2: Extract text
│   ├── preprocessing/          # Step 3: Chunking, cleaning, formatting
│   │   └── chunker.py
│   ├── embeddings/             # Step 4: Embedding and vector DB storage
│   │   └── embedder.py
│   ├── retrieval/              # Step 5: Retrieval logic
│   │   └── retriever.py
│   ├── generation/             # Step 6: LLM integration
│   │   └── generator.py
│   └── interface/              # FastAPI or Streamlit UI
│       └── api.py
├── main.py                     # 🔁 Entrypoint to glue modules together
├── requirements.txt
├── .env                        # Environment variables
├── .gitattributes              # Git attributes file to specify how Git should handle certain files. Helps maintain consistent line endings and file handling across different platforms
├── .gitignore                  # Files and folder mentioned in this file will not be uploaded on github
└── README.md
```

---

# Basic Configuration 

---

# Download local model from Huggingface

```
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "microsoft/phi-2"  # Replace with your choice from https://huggingface.co/models

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(model_id)

# Save model on local storage
model_save_path = "./models/phi-2"   # This should be configured as value for LOCAL_LLM_MODEL_PATH in .env file
model.save_pretrained(model_save_path)
tokenizer.save_pretrained(model_save_path)
```

---

## Required Environment Variables

Add the following variables to your `.env` file.  
**Comments indicate where to find each value in the Azure Portal or relevant service.**

```env
# Azure Blob Storage and Form Recognizer
AZURE_STORAGE_CONNECTION_STRING=      # Azure Portal > Storage Account > Access keys > Connection string
AZURE_STORAGE_ACCOUNT_KEY=           # Azure Portal > Storage Account > Access keys > key1/key2
AZURE_FORM_RECOGNIZER_ENDPOINT=      # Azure Portal > Form Recognizer > Keys and Endpoint > Endpoint
AZURE_FORM_RECOGNIZER_KEY=           # Azure Portal > Form Recognizer > Keys and Endpoint > Key

# Azure OpenAI Embedding
AZURE_OPENAI_EMBEDDING_API_KEY=      # Azure Portal > Azure OpenAI > Keys and Endpoint > Key
AZURE_OPENAI_EMBEDDING_ENDPOINT=     # Azure Portal > Azure OpenAI > Keys and Endpoint > Endpoint
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=   # Azure Portal > Azure OpenAI > Model Deployments > Deployment name
AZURE_OPENAI_EMBEDDING_VERSION=      # Azure Portal > Azure OpenAI > API version (e.g., 2023-05-15)

# Azure OpenAI Chat Completion
AZURE_OPENAI_CHAT_COMPLETION_API_KEY=      # Azure Portal > Azure OpenAI > Keys and Endpoint > Key
AZURE_OPENAI_CHAT_COMPLETION_ENDPOINT=     # Azure Portal > Azure OpenAI > Keys and Endpoint > Endpoint
AZURE_OPENAI_CHAT_COMPLETION_DEPLOYMENT=   # Azure Portal > Azure OpenAI > Model Deployments > Deployment name
AZURE_OPENAI_CHAT_COMPLETION_VERSION=      # Azure Portal > Azure OpenAI > API version (e.g., 2023-05-15)

# Azure AI Search
AZURE_SEARCH_ENDPOINT=              # Azure Portal > Cognitive Search > Overview > URL
AZURE_SEARCH_ADMIN_KEY=             # Azure Portal > Cognitive Search > Keys > Admin key
AZURE_SEARCH_INDEX_NAME=            # Azure Portal > Cognitive Search > Indexes > Index name

# Huggingface/Local Model Configuration
LOCAL_EMBEDDING_MODEL_NAME=         # Name of local Huggingface embedding model (if used)
LOCAL_VECTOR_DB_DIRECTORY=          # Directory path for local vector DB storage
LOCAL_LLM_MODEL_PATH=               # Path to local LLM model (if used)
```


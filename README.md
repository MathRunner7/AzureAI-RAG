# AzureAI-RAG
RAG Application using Azure AI

```text
AzureAI-RAG/
├── config/                     # 🔧 Config files (keys, endpoints, constants)
│   └── azure_config.py
├── data/                       # 📁 Raw files downloaded from Azure Blob (Stored Temporirily)
├── extracted/                  # 📄 Cleaned text from documents (Stored Temporirily)
├── vectorstore/                # 📦 Stored embeddings (FAISS or similar)
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
└── README.md
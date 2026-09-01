# Architecture & System Design

The **AI-Powered E-Commerce RAG Chatbot** is built using a modular, decoupled architecture consisting of a React + Vite frontend, a Python FastAPI backend, Sentence Transformers for embeddings, local FAISS for vector indexing, and Groq API for intent classification and answer generation.

## Component Overview Diagram

```mermaid
graph TD
    User([User Browser]) -->|HTTP REST API| ReactUI[React + Vite UI]
    
    subgraph Frontend Architecture
        ReactUI --> ChatHeader[ChatHeader Component]
        ReactUI --> ChatMessage[ChatMessage Component]
        ReactUI --> QuickActions[QuickActions Component]
        ReactUI --> DocumentUpload[DocumentUpload Component]
        ReactUI --> APIClient[api.js Client]
    end

    APIClient -->|POST /api/chat & /api/upload| FastAPIServer[FastAPI Backend]

    subgraph Backend Architecture
        FastAPIServer --> Routes[API Routes Controller]
        Routes --> IntentService[Intent Service]
        Routes --> RAGPipeline[RAG Pipeline Service]
        Routes --> DocService[PyMuPDF Document Service]
    end

    subgraph Groq Service Abstraction
        IntentService -->|Intent Classifier Prompt| GroqAPI[Groq API llama-3.3-70b-versatile]
        RAGPipeline -->|RAG Answer Prompt| GroqAPI
    end

    subgraph Vector Retrieval Engine
        DocService -->|Page Text & Metadata| SentenceEncoder[SentenceTransformers all-MiniLM-L6-v2]
        SentenceEncoder -->|384d Vectors| FAISS[FAISS Local Vector Store]
        RAGPipeline -->|Vector Search| FAISS
    end
```

## RAG Ingestion & Query Workflow

1. **Document Ingestion**:
   - `PyMuPDF` parses PDF files page-by-page.
   - Text is split into overlapping chunks while preserving sentence boundaries.
   - Each chunk retains metadata: `{ filename, page_number, chunk_id, text }`.
   - `SentenceTransformers` (`all-MiniLM-L6-v2`) converts text chunks into 384-dimensional dense vectors.
   - Embeddings and metadata are indexed in local `FAISS` vector store (`data/vector_store/`).

2. **Intent Classification & Routing**:
   - Every user message is analyzed by Groq API into 8 intents: `faq`, `product_question`, `product_recommendation`, `review_summary`, `order_shipping`, `returns_refunds`, `general_support`, `unknown`.
   - Dedicated prompt templates adjust guardrails based on the intent (e.g., forbidding product recommendations not present in retrieved context).

3. **Context Retrieval & Generation**:
   - Query embedding is searched against FAISS index using cosine similarity.
   - Top-K relevant document chunks are selected.
   - Prompt is sent to Groq `llama-3.3-70b-versatile`.
   - Response text, detected intent label, and citation cards (filename + page number) are returned to React UI.

# AI-Powered E-Commerce RAG Chatbot

A complete, production-ready **Retrieval-Augmented Generation (RAG)** e-commerce chatbot built with **FastAPI**, **Groq API** (`llama-3.3-70b-versatile`), **SentenceTransformers** (`all-MiniLM-L6-v2`), **FAISS**, **PyMuPDF**, and a modern **React + Vite** frontend.

---

## 1. Project Purpose & Features

This system provides automated customer support for e-commerce stores using knowledge-base documents:
- **Fact-Based Answering**: Answers questions using uploaded store knowledge base PDFs.
- **Page & Document Citations**: Shows exact source filename and page numbers for every answer.
- **8 Intent Categories**: Automatically categorizes user queries (`faq`, `product_question`, `product_recommendation`, `review_summary`, `order_shipping`, `returns_refunds`, `general_support`, `unknown`).
- **Dynamic Prompt Routing**: Adjusts answer guardrails based on intent (e.g. recommending only store-listed products, summarizing customer reviews, or explaining return windows).
- **PDF Ingestion & Vector Search**: Automatic page-by-page PDF text extraction, chunking with overlap, local embedding generation, and fast FAISS similarity search.
- **Web PDF Management**: Sidebar document manager for uploading extra PDFs and resetting the vector index.
- **Modern UI**: Styled with a White and Mid-Blue theme (`#2563EB`), quick action buttons, typing animations, and intent chips.

---

## 2. Architecture & RAG Flow

```text
React Frontend (Port 5173)
      ↓ REST API
FastAPI Backend (Port 8000)
      ↓
Intent Detection (Groq LLM / Fallback Classifier)
      ↓
Intent Router
      ├── FAQ / Policy Questions
      ├── Product Questions
      ├── Product Recommendations
      ├── Review Summaries
      └── General Support / Unknown
      ↓
RAG Retrieval Pipeline
      ↓
SentenceTransformer Embeddings (all-MiniLM-L6-v2)
      ↓
FAISS Local Vector Search
      ↓
Relevant PDF Chunks (with filename + page metadata)
      ↓
Groq LLM Answer Generation (llama-3.3-70b-versatile)
      ↓
Answer + Intent Chip + Citations returned to React UI
```

---

## 3. Prerequisites

Before running the project, ensure you have installed:
- **Python 3.10+** (Python 3.12 recommended)
- **Node.js 18+** & **npm 9+**
- **Groq API Key** (Free tier available at [console.groq.com](https://console.groq.com/))

---

## 4. How to Configure the Groq API Key

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and set your key:
   ```env
   GROQ_API_KEY=gsk_your_actual_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

---

## 5. How to Install & Start the FastAPI Backend

### Terminal 1: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server with Uvicorn
uvicorn app.main:app --reload --port 8000
```

---

## 6. How to Install & Start the React Frontend

### Terminal 2: Frontend Setup
```bash
cd frontend

# Install Node packages
npm install

# Start Vite development server
npm run dev
```

---

## 7. Exact Application URLs

- **React Web UI**: `http://localhost:5173`
- **FastAPI API Root**: `http://localhost:8000`
- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`

---

## 8. Default Knowledge Base Auto-Ingestion

On application startup, the backend checks for the default knowledge-base PDF located at:
```text
C:\Users\sakth\Downloads\ecommerce_chatbot_kb.pdf
```
It copies the file to `backend/data/uploads/ecommerce_chatbot_kb.pdf`, extracts text page-by-page using PyMuPDF, generates vector embeddings, and builds the local FAISS index automatically.

---

## 9. How to Upload Additional PDFs

1. Open the Web UI at `http://localhost:5173`.
2. Click the **Knowledge Base** button in the top header.
3. In the right drawer/modal, click **Select PDF File** or drop a new PDF document.
4. The system will extract text, chunk pages, generate embeddings, and instantly add the document to the active vector index.

---

## 10. Storage Locations for Uploads and Index

- **Uploaded PDFs**: `backend/data/uploads/`
- **FAISS Vector Store & Metadata**: `backend/data/vector_store/`
  - `faiss_index.bin`: Binary vector index.
  - `metadata.json`: Document registry and chunk metadata.

---

## 11. How to Reset the Knowledge Base

To clear custom uploads and re-index the default knowledge base:
- **UI Method**: Click **Knowledge Base** in the header -> Click **Reset Vector Index to Default**.
- **API Method**: Send a `POST` request to `http://localhost:8000/api/reset-index`.

---

## 12. Troubleshooting

| Issue | Solution |
|---|---|
| **Missing GROQ_API_KEY** | Ensure `.env` exists in `backend/` and contains a valid key. Fallback mode will display a warning if unconfigured. |
| **Failed Groq connection** | Check internet connectivity or inspect quota/rate limits on `console.groq.com`. |
| **PDF extraction failure** | Verify the PDF is readable. If it is password-protected, remove encryption before uploading. |
| **Scanned / Image PDFs** | PyMuPDF extracts text layers. Scanned PDFs without OCR text layers require pre-OCR processing. |
| **Frontend cannot connect to backend** | Verify backend is running on `http://localhost:8000`. Vite proxy routes `/api` calls to port 8000. |

---

## 13. Privacy & Security Explanation

- **Local Processing**: PDF text extraction, SentenceTransformer embedding generation (`all-MiniLM-L6-v2`), and FAISS vector database searches run **100% locally** on your machine.
- **External Transmission**: Only the retrieved context text relevant to the user query and the user's question are sent to the Groq API for response synthesis.

---

## 14. Summary of Key Commands

```bash
# 1. Start Backend Server
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --port 8000

# 2. Start Frontend UI
cd frontend
npm run dev

# 3. Build Frontend Production Bundle
cd frontend
npm run build
```

import os
import shutil
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import UPLOADS_DIR, DEFAULT_KB_SOURCE, DEFAULT_KB_DEST
from app.api.routes import router as api_router
from app.services.rag_service import rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Check if default knowledge base PDF exists and ingest if needed
    logger.info("Initializing E-Commerce RAG Backend Application...")
    try:
        if os.path.exists(DEFAULT_KB_SOURCE):
            if not os.path.exists(DEFAULT_KB_DEST):
                logger.info(f"Copying default KB source from '{DEFAULT_KB_SOURCE}' to '{DEFAULT_KB_DEST}'")
                shutil.copy(DEFAULT_KB_SOURCE, DEFAULT_KB_DEST)

            if os.path.exists(DEFAULT_KB_DEST):
                chunks_added, total_pages = rag_service.add_document(str(DEFAULT_KB_DEST))
                if chunks_added > 0:
                    logger.info(f"Auto-ingested default KB PDF: {chunks_added} chunks across {total_pages} pages.")
                else:
                    logger.info("Default KB PDF already indexed.")
        else:
            logger.warning(f"Default KB PDF source not found at '{DEFAULT_KB_SOURCE}'. Skipping auto-ingestion.")
    except Exception as e:
        logger.error(f"Error during default KB auto-ingestion startup: {e}")

    yield
    logger.info("Shutting down backend server.")

app = FastAPI(
    title="AI-Powered E-Commerce RAG Chatbot API",
    description="FastAPI Backend for E-Commerce RAG Chatbot powered by Groq LLM, PyMuPDF, SentenceTransformers, and FAISS.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API endpoints
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "AI-Powered E-Commerce RAG Chatbot API is online.",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

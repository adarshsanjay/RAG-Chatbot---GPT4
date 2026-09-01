import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    DocumentListResponse,
    UploadResponse,
    DocumentMetadata
)
from app.config import UPLOADS_DIR, DEFAULT_KB_SOURCE, DEFAULT_KB_DEST
from app.services.rag_service import rag_service
from app.services.groq_service import groq_service

logger = logging.getLogger("api_routes")
router = APIRouter(prefix="/api")

@router.get("/health", response_model=HealthResponse)
def get_health():
    docs = rag_service.get_indexed_documents()
    return HealthResponse(
        status="ok",
        indexed_documents_count=len(docs),
        total_chunks=len(rag_service.metadata),
        groq_api_configured=groq_service.is_configured(),
        embedding_model="all-MiniLM-L6-v2"
    )

@router.get("/documents", response_model=DocumentListResponse)
def get_documents():
    docs_raw = rag_service.get_indexed_documents()
    doc_models = [
        DocumentMetadata(
            filename=d["filename"],
            total_pages=d["total_pages"],
            total_chunks=d["total_chunks"],
            file_size_bytes=d.get("file_size_bytes", 0),
            indexed_at=d.get("indexed_at", "")
        )
        for d in docs_raw
    ]
    return DocumentListResponse(
        documents=doc_models,
        total_chunks=len(rag_service.metadata)
    )

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = UPLOADS_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks_added, total_pages = rag_service.add_document(str(file_path))
        msg = f"Successfully uploaded '{file.filename}' and added {chunks_added} chunks across {total_pages} pages."
        if chunks_added == 0:
            msg = f"File '{file.filename}' was already indexed."

        return UploadResponse(
            message=msg,
            filename=file.filename,
            total_pages=total_pages,
            chunks_added=chunks_added
        )
    except Exception as e:
        logger.error(f"Error processing uploaded PDF: {e}")
        # Clean up corrupted file if saved
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse PDF '{file.filename}'. Please ensure it is a valid, unencrypted PDF document."
        )

@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        history_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.history or [])
        ]
        answer, intent, sources = rag_service.answer_query(request.message, history_dicts)
        return ChatResponse(
            answer=answer,
            intent=intent,
            sources=sources
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")

@router.post("/reset-index")
def reset_index():
    try:
        rag_service.reset_index()
        # Clean uploads dir
        for item in os.listdir(UPLOADS_DIR):
            item_path = os.path.join(UPLOADS_DIR, item)
            if os.path.isfile(item_path):
                os.remove(item_path)

        # Re-ingest default PDF if available
        reindexed_count = 0
        if os.path.exists(DEFAULT_KB_SOURCE):
            shutil.copy(DEFAULT_KB_SOURCE, DEFAULT_KB_DEST)
            chunks_added, _ = rag_service.add_document(str(DEFAULT_KB_DEST))
            reindexed_count = chunks_added

        return {
            "status": "success",
            "message": f"Index reset complete. Re-indexed default KB document ({reindexed_count} chunks)."
        }
    except Exception as e:
        logger.error(f"Failed to reset index: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to reset index: {str(e)}")

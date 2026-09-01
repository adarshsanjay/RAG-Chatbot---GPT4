from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User question or statement")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Recent chat history")

class SourceCitation(BaseModel):
    filename: str = Field(..., description="Document source filename")
    page: int = Field(..., description="Page number (1-indexed)")
    snippet: Optional[str] = Field(None, description="Relevant context snippet")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="Generated LLM response")
    intent: str = Field(..., description="Detected user intent")
    sources: List[SourceCitation] = Field(default_factory=list, description="List of source citations")

class DocumentMetadata(BaseModel):
    filename: str
    total_pages: int
    total_chunks: int
    file_size_bytes: int
    indexed_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_chunks: int

class HealthResponse(BaseModel):
    status: str
    indexed_documents_count: int
    total_chunks: int
    groq_api_configured: bool
    embedding_model: str

class UploadResponse(BaseModel):
    message: str
    filename: str
    total_pages: int
    chunks_added: int

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

from app.config import VECTOR_STORE_DIR, EMBEDDING_MODEL_NAME
from app.services.groq_service import groq_service
from app.services.intent_service import intent_service
from app.services.document_service import document_service

logger = logging.getLogger("rag_service")

class RAGService:
    def __init__(self):
        self.vector_store_dir = VECTOR_STORE_DIR
        self.index_path = os.path.join(self.vector_store_dir, "faiss_index.bin")
        self.metadata_path = os.path.join(self.vector_store_dir, "metadata.json")

        # Load embedding model
        logger.info(f"Loading SentenceTransformer model: {EMBEDDING_MODEL_NAME}")
        self.encoder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        if hasattr(self.encoder, "get_embedding_dimension"):
            self.embedding_dim = self.encoder.get_embedding_dimension()
        else:
            self.embedding_dim = self.encoder.get_sentence_embedding_dimension()

        # FAISS index and metadata store
        self.index = None
        self.metadata: List[Dict[str, Any]] = []
        self.indexed_files: Dict[str, Dict[str, Any]] = {} # filename -> file metadata

        self._load_vector_store()

    def _load_vector_store(self):
        """Loads FAISS index and metadata from disk if available."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            try:
                self.index = faiss.read_index(self.index_path)
                with open(self.metadata_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.metadata = data.get("chunks", [])
                    self.indexed_files = data.get("files", {})
                logger.info(f"Loaded FAISS vector store with {len(self.metadata)} chunks across {len(self.indexed_files)} files.")
            except Exception as e:
                logger.error(f"Failed to load existing vector store: {e}. Re-initializing empty store.")
                self._initialize_empty_store()
        else:
            self._initialize_empty_store()

    def _initialize_empty_store(self):
        self.index = faiss.IndexFlatIP(self.embedding_dim) # Cosine similarity with normalized vectors
        self.metadata = []
        self.indexed_files = {}

    def _save_vector_store(self):
        """Persists FAISS index and metadata to disk."""
        os.makedirs(self.vector_store_dir, exist_ok=True)
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "files": self.indexed_files,
                "chunks": self.metadata
            }, f, indent=2)
        logger.info("Saved FAISS vector store and metadata to disk.")

    def is_file_indexed(self, filename: str, file_hash: Optional[str] = None) -> bool:
        if filename in self.indexed_files:
            if file_hash and self.indexed_files[filename].get("hash") == file_hash:
                return True
            if not file_hash:
                return True
        return False

    def add_document(self, file_path: str, force_reindex: bool = False) -> Tuple[int, int]:
        """
        Indexes a PDF file.
        Returns: (chunks_added, total_pages)
        """
        filename = os.path.basename(file_path)
        file_hash = document_service.calculate_file_hash(file_path)

        if not force_reindex and self.is_file_indexed(filename, file_hash):
            logger.info(f"File '{filename}' is already indexed. Skipping.")
            file_meta = self.indexed_files[filename]
            return 0, file_meta.get("total_pages", 0)

        chunks, total_pages = document_service.process_pdf(file_path)
        if not chunks:
            logger.warning(f"No text extracted from '{filename}'.")
            return 0, total_pages

        # Generate embeddings
        texts = [c["text"] for c in chunks]
        embeddings = self.encoder.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

        # Add to FAISS index
        self.index.add(embeddings.astype(np.float32))
        self.metadata.extend(chunks)

        # Update file index registry
        file_size = os.path.getsize(file_path)
        self.indexed_files[filename] = {
            "filename": filename,
            "hash": file_hash,
            "total_pages": total_pages,
            "total_chunks": len(chunks),
            "file_size_bytes": file_size,
            "indexed_at": datetime.now().isoformat()
        }

        self._save_vector_store()
        return len(chunks), total_pages

    def retrieve(self, query: str, top_k: int = 4, score_threshold: float = 0.25) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant chunks matching the query above a similarity threshold."""
        if not self.metadata or self.index is None or self.index.ntotal == 0:
            return []

        query_vec = self.encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True).astype(np.float32)
        scores, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            if score >= score_threshold:
                item = dict(self.metadata[idx])
                item["score"] = float(score)
                results.append(item)

        return results

    def reset_index(self):
        """Clears all vector store indices and metadata."""
        self._initialize_empty_store()
        self._save_vector_store()
        logger.info("Vector store reset complete.")

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        return list(self.indexed_files.values())

    def answer_query(self, query: str, history: List[Dict[str, str]] = None) -> Tuple[str, str, List[Dict[str, Any]]]:
        """
        Full RAG Pipeline:
        1. Detect intent using IntentService
        2. Retrieve relevant context chunks from FAISS
        3. Build intent-customized prompt
        4. Generate response via Groq API
        5. Return (answer_text, detected_intent, source_citations)
        """
        # Step 1: Detect intent
        intent = intent_service.detect_intent(query, history)
        logger.info(f"Query: '{query}' | Detected Intent: {intent}")

        # Step 2: Retrieve context chunks
        chunks = self.retrieve(query, top_k=4)

        # Build citations
        sources = []
        seen_citations = set()
        context_blocks = []

        for c in chunks:
            cite_key = (c["filename"], c["page"])
            if cite_key not in seen_citations:
                seen_citations.add(cite_key)
                sources.append({
                    "filename": c["filename"],
                    "page": c["page"],
                    "snippet": c["text"][:150] + "..."
                })
            context_blocks.append(f"--- Document: {c['filename']} | Page: {c['page']} ---\n{c['text']}")

        context_str = "\n\n".join(context_blocks) if context_blocks else "NO RELEVANT KNOWLEDGE BASE CONTENT FOUND."

        # Step 3: Build intent-specific system prompt & guidelines
        intent_instruction = self._get_intent_instruction(intent)

        system_prompt = f"""You are an AI-powered E-Commerce Customer Support Assistant.
Your primary role is to answer questions strictly based on the provided Knowledge Base Context below.

=== INTENT DIRECTIVE ===
Detected Intent: {intent.upper()}
{intent_instruction}

=== KNOWLEDGE BASE CONTEXT ===
{context_str}

=== STRICT RAG RULES ===
1. Answer using ONLY facts explicitly stated in the Knowledge Base Context above.
2. If no relevant evidence exists in the context to answer the query, state clearly: "I cannot find information regarding this in the uploaded knowledge base."
3. Never fabricate or extrapolate details outside the document context.
4. Keep the tone polite, clear, structured, and helpful for e-commerce shoppers.
5. If citations are available, seamlessly incorporate reference page numbers if applicable.
"""

        # Format recent conversation history (max 6 turns)
        formatted_messages = []
        if history:
            for turn in history[-6:]:
                formatted_messages.append({"role": turn["role"], "content": turn["content"]})
        formatted_messages.append({"role": "user", "content": query})

        # Step 4: Generate completion from Groq Service
        answer = groq_service.generate_chat_completion(
            messages=formatted_messages,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=800
        )

        return answer, intent, sources

    def _get_intent_instruction(self, intent: str) -> str:
        instructions = {
            "product_recommendation": (
                "Recommend ONLY products explicitly described in the retrieved knowledge base context. "
                "If product details or alternatives are not found in the context, explicitly inform the user that no recommendations are available in the knowledge base."
            ),
            "review_summary": (
                "Summarize ONLY customer reviews or ratings present in the retrieved context. "
                "Do not invent buyer feedback or star ratings."
            ),
            "returns_refunds": (
                "Provide precise return, refund, replacement, or cancellation policy information exactly as specified in the context. "
                "Include timelines (e.g. return window, refund processing days) if available."
            ),
            "order_shipping": (
                "Provide step-by-step guidance on order placement, order status tracking, shipping options, and courier details present in the context."
            ),
            "product_question": (
                "Answer specific product questions (specs, warranty, stock status, size charts, authenticity) strictly using context details."
            ),
            "faq": (
                "Answer general platform, payment, security, or account questions using context details."
            ),
            "general_support": (
                "Assist with customer care, contact details, or polite greetings using knowledge base context where relevant."
            ),
            "unknown": (
                "The user query could not be categorized into a standard e-commerce flow or context is missing. "
                "State politely that the knowledge base does not cover this topic and ask if they need assistance with products, orders, shipping, or returns."
            )
        }
        return instructions.get(intent, "Answer strictly based on retrieved context.")

rag_service = RAGService()

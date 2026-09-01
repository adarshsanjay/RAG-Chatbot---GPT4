import os
import hashlib
import logging
from typing import List, Dict, Any, Tuple
import pymupdf  # PyMuPDF

logger = logging.getLogger("document_service")

class DocumentService:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def calculate_file_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def process_pdf(self, file_path: str) -> Tuple[List[Dict[str, Any]], int]:
        """
        Parses PDF page by page using PyMuPDF and returns chunks with metadata.
        Returns: (chunks_list, total_pages)
        Each chunk is a dict: {
            "chunk_id": str,
            "filename": str,
            "page": int,
            "text": str
        }
        """
        filename = os.path.basename(file_path)
        doc = pymupdf.open(file_path)
        total_pages = len(doc)
        all_chunks = []

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1  # 1-indexed
            text = page.get_text("text").strip()

            if not text:
                continue

            page_chunks = self._chunk_text(text, filename, page_num)
            all_chunks.extend(page_chunks)

        doc.close()
        logger.info(f"Processed '{filename}': {total_pages} pages, {len(all_chunks)} chunks.")
        return all_chunks, total_pages

    def _chunk_text(self, text: str, filename: str, page_num: int) -> List[Dict[str, Any]]:
        """
        Splits text into overlapping chunks while preserving sentence/paragraph structure where possible.
        """
        chunks = []
        if len(text) <= self.chunk_size:
            chunk_id = f"{filename}_p{page_num}_c0"
            chunks.append({
                "chunk_id": chunk_id,
                "filename": filename,
                "page": page_num,
                "text": text
            })
            return chunks

        # Split into paragraphs/lines first
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        current_chunk = ""
        chunk_idx = 0

        for line in lines:
            if len(current_chunk) + len(line) + 1 <= self.chunk_size:
                if current_chunk:
                    current_chunk += " " + line
                else:
                    current_chunk = line
            else:
                if current_chunk:
                    chunk_id = f"{filename}_p{page_num}_c{chunk_idx}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "filename": filename,
                        "page": page_num,
                        "text": current_chunk
                    })
                    chunk_idx += 1
                    # Retain overlap from end of current chunk
                    overlap_start = max(0, len(current_chunk) - self.chunk_overlap)
                    current_chunk = current_chunk[overlap_start:] + " " + line
                else:
                    # Single very long line
                    current_chunk = line

        if current_chunk:
            chunk_id = f"{filename}_p{page_num}_c{chunk_idx}"
            chunks.append({
                "chunk_id": chunk_id,
                "filename": filename,
                "page": page_num,
                "text": current_chunk
            })

        return chunks

document_service = DocumentService()

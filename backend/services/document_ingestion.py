import io
import os
import hashlib
from typing import List, Dict
from pypdf import PdfReader
from fastapi import UploadFile
from .text_utils import chunk_text
from vectorstores.chroma_store import ChromaVectorStore
from db.database import SessionLocal
from db.models import Document, Chunk
import json
from services.enrichment import enrich_document, enrich_chunk

CASE_FILES_COLLECTION = os.getenv("CASE_FILES_COLLECTION", "case_files")
case_files_store = ChromaVectorStore(collection_name=CASE_FILES_COLLECTION)

SUPPORTED_TEXT_TYPES = {"text/plain"}
SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_DOCX_TYPES = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}

try:
    import docx  # python-docx
    _DOCX_AVAILABLE = True
except ImportError:
    _DOCX_AVAILABLE = False

MAX_DOC_LENGTH = 50_000  # safety cutoff
RAW_DIR = os.getenv("RAW_STORAGE", "storage/raw")
CURATED_DIR = os.getenv("CURATED_STORAGE", "storage/curated")
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CURATED_DIR, exist_ok=True)


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def _extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages_text)


def _extract_text_from_docx(content: bytes) -> str:
    if not _DOCX_AVAILABLE:
        return ""
    bio = io.BytesIO(content)
    document = docx.Document(bio)
    return "\n".join(p.text for p in document.paragraphs)


def ingest_upload(file: UploadFile) -> Dict:
    raw = file.file.read()
    file.file.seek(0)
    file_hash = _hash_bytes(raw)
    filename = file.filename or f"uploaded_{file_hash}.dat"
    content_type = file.content_type or "application/octet-stream"
    if content_type in SUPPORTED_PDF_TYPES or filename.lower().endswith(".pdf"):
        text = _extract_text_from_pdf(raw)
        source_type = "upload_pdf"
    elif (content_type in SUPPORTED_DOCX_TYPES or filename.lower().endswith(".docx")) and _DOCX_AVAILABLE:
        text = _extract_text_from_docx(raw)
        source_type = "upload_docx"
    elif content_type in SUPPORTED_TEXT_TYPES:
        text = raw.decode("utf-8", errors="ignore")
        source_type = "upload_text"
    else:
        return {"status": "ignored", "reason": f"Unsupported type {content_type}"}
    text = text[:MAX_DOC_LENGTH]
    raw_path = os.path.join(RAW_DIR, f"{file_hash}_{filename}")
    if not os.path.exists(raw_path):
        with open(raw_path, "wb") as f:
            f.write(raw)
    # Enrichment (document level)
    doc_meta_enriched, _ = enrich_document(text, filename)
    # Chunk
    chunks = chunk_text(text, size=3000, overlap=250)
    metadatas = []
    chunk_meta_jsons = []
    for i, ch in enumerate(chunks):
        per_chunk = enrich_chunk(ch, doc_meta_enriched)
        base_meta = {"filename": filename, "hash": file_hash, "chunk_index": i, "source_type": source_type}
        base_meta.update(per_chunk)
        metadatas.append(base_meta)
        chunk_meta_jsons.append(json.dumps(per_chunk))
    ids = case_files_store.add_texts(chunks, metadatas=metadatas)
    db = SessionLocal()
    try:
        meta_json = {"size": len(raw)}
        meta_json.update(doc_meta_enriched)
        doc = Document(
            filename=filename,
            hash=file_hash,
            content_type=content_type,
            source=source_type,
            raw_path=raw_path,
            meta_json=json.dumps(meta_json)
        )
        db.add(doc)
        db.flush()
        chunk_rows = [
            Chunk(document_id=doc.id, chunk_index=i, text=chunk_text_value, vector_id=vector_id, meta_json=chunk_meta_jsons[i])
            for i, (chunk_text_value, vector_id) in enumerate(zip(chunks, ids))
        ]
        db.add_all(chunk_rows)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
    return {"status": "ok", "filename": filename, "chunks": len(chunks), "vector_ids": ids, "hash": file_hash, "enriched": True}


def ingest_crawled_case(case_id: str, text: str, source_url: str) -> Dict:
    """Ingest a crawled case law document (already plain text)."""
    raw_bytes = text.encode("utf-8", errors="ignore")
    file_hash = _hash_bytes(raw_bytes)
    filename = f"case_{case_id}.txt"
    text = text[:MAX_DOC_LENGTH]
    raw_path = os.path.join(RAW_DIR, f"{file_hash}_{filename}")
    if not os.path.exists(raw_path):
        with open(raw_path, "wb") as f:
            f.write(raw_bytes)
    doc_meta_enriched, _ = enrich_document(text, filename)
    chunks = chunk_text(text, size=3000, overlap=250)
    metadatas = []
    chunk_meta_jsons = []
    for i, ch in enumerate(chunks):
        per_chunk = enrich_chunk(ch, doc_meta_enriched)
        base_meta = {"filename": filename, "hash": file_hash, "chunk_index": i, "source_type": "crawl_case_law", "url": source_url}
        base_meta.update(per_chunk)
        metadatas.append(base_meta)
        chunk_meta_jsons.append(json.dumps(per_chunk))
    ids = case_files_store.add_texts(chunks, metadatas=metadatas)
    db = SessionLocal()
    try:
        meta_json = {"size": len(raw_bytes), "url": source_url}
        meta_json.update(doc_meta_enriched)
        doc = Document(
            filename=filename,
            hash=file_hash,
            content_type="text/plain",
            source="crawl",
            raw_path=raw_path,
            meta_json=json.dumps(meta_json)
        )
        db.add(doc)
        db.flush()
        chunk_rows = [
            Chunk(document_id=doc.id, chunk_index=i, text=chunk_text_value, vector_id=vector_id, meta_json=chunk_meta_jsons[i])
            for i, (chunk_text_value, vector_id) in enumerate(zip(chunks, ids))
        ]
        db.add_all(chunk_rows)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
    return {"status": "ok", "filename": filename, "chunks": len(chunks), "vector_ids": ids, "hash": file_hash, "enriched": True, "url": source_url}

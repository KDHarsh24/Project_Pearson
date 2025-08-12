import json
import re
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from db.models import Document, Chunk

DATE_PATTERNS = [
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
]
DATE_REGEX = re.compile("|".join(DATE_PATTERNS))


def _normalize_date(raw: str) -> Optional[str]:
    parts = re.split(r"[/-]", raw)
    if len(parts) != 3:
        return None
    d, m, y = parts
    if len(y) == 2:
        y = ("20" if int(y) < 50 else "19") + y
    try:
        dt = datetime(int(y), int(m), int(d))
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def build_timeline(db: Session, filename: str | None = None, file_hash: str | None = None):
    q = db.query(Document)
    if filename:
        q = q.filter(Document.filename == filename)
    if file_hash:
        q = q.filter(Document.hash == file_hash)
    docs = q.limit(20).all()
    events: List[Dict] = []
    for doc in docs:
        # Scan chunks for dates
        for ch in doc.chunks[:300]:
            for match in DATE_REGEX.findall(ch.text or ""):
                norm = _normalize_date(match)
                if not norm:
                    continue
                snippet = ch.text[:180].replace("\n", " ")
                events.append({
                    "date": norm,
                    "raw": match,
                    "document": doc.filename,
                    "chunk_index": ch.chunk_index,
                    "snippet": snippet
                })
    # Sort
    events.sort(key=lambda e: e["date"]) if events else None
    return {"count": len(events), "events": events[:500]}

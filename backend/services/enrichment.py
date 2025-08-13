import re
from typing import List, Dict, Tuple

# Lightweight regex-based enrichment (no heavy NLP dependency) for hackathon speed.
# Can later be upgraded to spaCy / Watson NLP.

# Common Indian legal citation patterns (simplified)
CITATION_PATTERNS = [
    r"AIR\s*\d{4}\s*[A-Z]{2,}[^\s]*\s*\d+",   # AIR 1996 SC 123
    r"\d{4}\s*SCC\s*\d+",                       # 2012 SCC 455
    r"\(\d{4}\)\s*\d+\s*SCC\s*\d+",          # (2013) 5 SCC 488
    r"\d{4}\s*Cri\s*LJ\s*\d+",                 # 2001 Cri LJ 455
]
CITATION_REGEX = re.compile("|".join(CITATION_PATTERNS))

# Statute / section references
SECTION_REGEX = re.compile(r"(Section|Sec\.)\s+\d+[A-Za-z0-9()/-]*")
ACT_REGEX = re.compile(r"[A-Z][A-Za-z ]+ Act,? \d{4}")

# Dates (basic)
DATE_REGEX = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b")

# Judge indicators (lines containing 'J.' or 'Justice')
JUDGE_REGEX = re.compile(r"Justice\s+[A-Z][A-Za-z. ]+|[A-Z][A-Za-z]+\s+J\.")

# Party style (e.g., SOME NAME v. SOME NAME)
PARTY_STYLE_REGEX = re.compile(r"([A-Z][A-Z .&']+\s+v\.\s+[A-Z][A-Z .&']+)")


def _dedupe(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for s in seq:
        if not s:
            continue
        k = s.strip()
        if k not in seen:
            seen.add(k)
            out.append(k)
    return out


def enrich_document(full_text: str, filename: str) -> Tuple[Dict, List[Dict]]:
    """Return (doc_level_metadata, per_chunk_metadata_placeholders[]) without chunk text.
    Chunk metadata will be merged later with core chunk info.
    """
    citations = _dedupe(CITATION_REGEX.findall(full_text))
    sections = _dedupe(SECTION_REGEX.findall(full_text))
    acts = _dedupe(ACT_REGEX.findall(full_text))
    dates = _dedupe(DATE_REGEX.findall(full_text))
    parties = _dedupe(PARTY_STYLE_REGEX.findall(full_text))
    judges = _dedupe(JUDGE_REGEX.findall(full_text))

    doc_meta = {
        "filename": filename,
        "citations": citations[:50],
        "sections": sections[:50],
        "acts": acts[:50],
        "dates": dates[:100],
        "parties": parties[:20],
        "judges": judges[:20],
    }
    return doc_meta, []  # per-chunk enrichment (advanced NLP) can be added later


def enrich_chunk(chunk_text: str, doc_meta: Dict) -> Dict:
    """Light per-chunk enrichment (can be extended)."""
    # Capture citations appearing inside this chunk
    local_citations = CITATION_REGEX.findall(chunk_text)
    local_sections = SECTION_REGEX.findall(chunk_text)
    return {
        "citations_local": _dedupe(local_citations)[:10],
        "sections_local": _dedupe(local_sections)[:10],
    }

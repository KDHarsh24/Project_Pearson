from typing import List, Dict, Any
import os
from vectorstores.chroma_store import ChromaVectorStore

CASE_FILES_COLLECTION = os.getenv("CASE_FILES_COLLECTION", "case_files")
CASE_LAW_COLLECTION = os.getenv("CASE_LAW_COLLECTION", "legal_cases")

case_files_store = ChromaVectorStore(collection_name=CASE_FILES_COLLECTION)
case_law_store = ChromaVectorStore(collection_name=CASE_LAW_COLLECTION)


def hybrid_search(query: str, k_case_files: int = 3, k_case_law: int = 3, filters: Dict[str, Any] | None = None) -> Dict[str, List[Dict]]:
    case_files_hits = case_files_store.similarity_search(query, k=k_case_files)
    case_law_hits = case_law_store.similarity_search(query, k=k_case_law)
    if filters:
        def _match(meta):
            for k, v in filters.items():
                if str(meta.get(k)) != str(v):
                    return False
            return True
        case_files_hits = [h for h in case_files_hits if _match(h["metadata"]) ]
        case_law_hits = [h for h in case_law_hits if _match(h["metadata"]) ]
    return {"case_files": case_files_hits, "case_law": case_law_hits}

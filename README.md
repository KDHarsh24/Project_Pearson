# Project Pearson – Mike Ross AI Engine (Hackathon Edition)

## 1. Vision
Agentic legal AI stack on IBM watsonx: ingest + govern (watsonx.data style), retrieve (vector + metadata hybrid), reason (Granite), act (modular agents). Focus scope: Mike Ross layer (Case Breaker, Contract X-Ray seed, Deposition Strategist seed, Precedent Strategist foundation).

## 2. Current Implemented Components
- FastAPI service (`main.py`) with upload + RAG chat (hybrid search over case law + uploaded files).
- Crawler (`app.py`) for indiankanoon.org seeding `legal_cases` vector collection.
- Unified Chroma persistent vector store abstraction (`vectorstores/chroma_store.py`).
- Dual collections: `legal_cases` (precedent corpus) and `case_files` (user uploads).
- Ingestion pipeline (`services/document_ingestion.py`): PDF/text parse -> chunk -> enrich -> embed -> vector IDs -> SQLite persistence.
- Enrichment (`services/enrichment.py`): regex-based citations, sections, acts, judges, parties extraction (upgrade path to NLP models).
- Retrieval service (`services/retrieval.py`): hybrid search across both collections + metadata post-filter.
- SQLite schema (`db/models.py`) storing documents + chunks with linkage to vector IDs & enriched meta JSON.

## 3. Data Lakehouse Layout (Local Hackathon Form)
```
storage/
  raw/        # exact ingested files
  curated/    # cleaned / normalized (future)
  feature/    # derived artifacts (timelines, graphs, clause JSON)
vector/       # chroma persistent directories (VECTOR_DB_PATH)
pearson.db    # metadata + chunk registry
```
Evolution path:
- Replace local dirs with object storage (IBM Cloud Object Storage) + Iceberg/Hudi tables via watsonx.data connectors.
- Add governance (row-level lineage, PII masking) hooks.

## 4. Vector Store Strategy
- Embeddings: IBM `ibm/slate-30m-english-rtrvr` via watsonx.
- Chroma persistent client, collection per corpus.
- ID schema: `doc_<epoch>_<i>` ensures uniqueness across runs.
- Metadata keys (uploads): `filename`, `hash`, `chunk_index`, `citations_local`, `sections_local`, enriched doc-level meta persisted in DB.
- Metadata keys (case law): `source`, `chunk_index`.

## 5. RAG Flow (Upload to Answer)
1. Upload file -> ingestion service extracts raw text + chunks.
2. Enrichment extracts citations, acts, parties, judges.
3. Each chunk embedded + stored (case_files collection); DB + meta JSON updated.
4. Chat request (use_rag=true) -> hybrid retrieval (k from each collection) -> optional metadata filter.
5. Retrieved snippets injected as system context with source tags -> Granite chat model response (with citations expectation).

## 6. Mike Ross Modules Roadmap
### 6.1 Case Breaker (In Progress)
- DONE: Basic ingestion + enrichment + retrieval.
- NEXT: Entity graph (networkx) + timeline builder from dates & citations.
### 6.2 Contract X-Ray (Planned Seed)
- Clause segmentation, risk rule baseline; diff vs firm playbook (future JSON spec).
### 6.3 Deposition Strategist (Planned Seed)
- Witness profile aggregation, inconsistency detection (cross-chunk contradiction scan).
### 6.4 Precedent Strategist (Foundation Ready)
- Semantic precedent search (legal_cases collection) now active.
- NEXT: Argument / statute / reasoning extraction + ranking, judge profiling, adverse authority detection.

## 7. Incremental Task Board
| Phase | Tasks |
|-------|-------|
| P1 | (DONE) Persistent vector + SQLite; hybrid RAG; crawler integration; enrichment v1 |
| P2 | Entity & citation graph; timeline synthesis; retrieval filter params exposed in API |
| P3 | Precedent Strategist argument extraction (LLM pass) + ranking; judge stats aggregation |
| P4 | Contract X-Ray prototype (clause extraction + risk diffs) |
| P5 | Deposition Strategist inconsistency + question suggestion; adverse authority scan |
| P6 | Advanced hybrid (BM25 + dense) + reranking; caching layer |

## 8. Environment & Config
`.env` keys:
```
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=
VECTOR_DB_PATH=legal_cases_store
CASE_LAW_COLLECTION=legal_cases
CASE_FILES_COLLECTION=case_files
SQLITE_PATH=pearson.db
RAW_STORAGE=storage/raw
CURATED_STORAGE=storage/curated
```
Run backend: `./run.sh`

## 9. Retrieval Usage
`POST /chat` form fields: `user_input`, `session_id`, `use_rag` (bool). Future: `filters` JSON.

## 10. Developer Scripts
- `app.py`: run crawler seed (legal precedent ingestion).
- `run.sh`: environment bootstrap + uvicorn.

## 11. Enrichment Details
Regex-based (fast): citations, sections, acts, dates, parties, judges. Per-chunk local citations/sections retained for targeted retrieval and future highlighting.

## 12. Next Immediate Steps (Kickoff P2)
- Add API for metadata-driven filtered search.
- Build `services/graph_builder.py` for entity co-occurrence graph (parties, judges).
- Build timeline synthesizer (extract normalized date events + snippet context).
- Add reranker (LLM or cosine threshold) to tighten top-k results.

---
Hackathon goal: rock-solid ingestion + high-signal retrieval + explainable answers with citations.
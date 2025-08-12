# Project Pearson – Mike Ross AI Engine (Hackathon Edition)

## 1. Overview
Agentic RAG system for paralegal intelligence ("Mike Ross"). Focus: high-signal ingestion, enrichment, retrieval, explainable answers (citations).

## 2. Environment (.env)
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

## 3. Components
- FastAPI service (`main.py`) – upload, chat (RAG), search, graph, timeline.
- Crawler / seeder (`app.py`) – ingest public case law.
- Vector store wrapper (`vectorstores/chroma_store.py`).
- Document ingestion (`services/document_ingestion.py`).
- Enrichment (`services/enrichment.py`) – regex-based legal signal.
- Retrieval (`services/retrieval.py`) – hybrid across case files + case law.
- Graph (`services/graph_builder.py`) – co-occurrence network.
- Timeline (`services/timeline.py`) – date event extraction.
- DB (`db/models.py`, `db/database.py`) – SQLite metadata + chunk index.

## 4. Data Lakehouse Layers (hackathon-light)
- Raw Layer: exact uploads / crawled text (`storage/raw`).
- Curated Layer: enriched structured metadata (future). Current enrichment persisted in SQLite JSON fields.
- Vector Layer: Chroma persistent collections (two: case_files, legal_cases).

## 5. Ingestion Flows
### 5.1 Uploaded Case Files
1. Upload via `/upload/`.
2. File hashed; raw bytes saved to Raw layer.
3. Text extraction (PDF / DOCX / TXT) -> truncate safety.
4. Document-level enrichment (citations, sections, acts, dates, parties, judges).
5. Chunking (3000 chars, 250 overlap).
6. Per-chunk enrichment (local citations/sections) merged into metadata.
7. Embeddings via WatsonX embeddings model -> Chroma (case_files collection).
8. Metadata + chunk linkage stored in SQLite.

### 5.2 Crawled Case Law
1. `app.py` crawler hits indiankanoon seed pages.
2. HTML -> cleaned text.
3. Same enrichment + chunk pipeline.
4. Stored in Chroma (legal_cases collection) and SQLite with source url.

## 6. Retrieval (RAG)
`/chat` with `use_rag=true`:
- Vector search top-k from both collections.
- Scores transformed from distances; context block assembled with source + snippet.
- Injected into system message for answer synthesis (citations expected).

## 7. Auxiliary Intelligence
- Entity Graph: aggregate parties / judges / acts / sections for relationship insights.
- Timeline: normalize and order date mentions per document or overall.

## 8. Extensibility Roadmap (Mike Ross Modules)
1. Case Breaker – add semantic filters (party, act) + contradiction detector.
2. Contract X-Ray – clause segmentation + risk ruleset + re-draft prompts.
3. Deposition Strategist – witness dossier aggregation + inconsistency surfacing.
4. Precedent Strategist – similarity expansion + argument extraction.

## 9. Retrieval Usage
`POST /chat` form fields: `user_input`, `session_id`, `use_rag` (bool). Optional future: `filters` JSON.

## 10. Developer Scripts
- `app.py` – run to crawl & ingest precedent.
- `run.sh` – environment bootstrap + uvicorn.

## 11. Enrichment Details
Regex-based (fast): citations, sections, acts, dates, parties, judges. Per-chunk local citations/sections retained for targeted retrieval and future highlighting.

## 12. Quick Start
```
./run.sh            # create venv, install, start API (port 8000)
python app.py       # seed legal case law (adjust MAX_PAGES)
```
Upload test:
```
curl -F "file=@sample.pdf" -F "session_id=abc123" http://localhost:8000/upload/
```
Chat with RAG:
```
curl -F "user_input=What are key arguments?" -F "session_id=abc123" -F "use_rag=true" http://localhost:8000/chat/
```

## 13. Current Hackathon Focus
- Solid ingestion & metadata.
- Fast retrieval with explainability.
- Modular expansion points prepared.

---
Hackathon goal: rock-solid ingestion + high-signal retrieval + explainable answers with citations.

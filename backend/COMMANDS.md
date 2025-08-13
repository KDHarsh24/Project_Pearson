# Backend Command Reference (Updated with watsonx RAG Integration)

Concise list of useful commands, what they do, and when to use them. Run all commands from the `backend/` directory unless noted.

## 0. Required .env Keys
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
WATSONX_URL=https://us-south.ml.cloud.ibm.com
VECTOR_DB_PATH=legal_cases_store
CASE_LAW_COLLECTION=legal_cases
CASE_UPLOAD_COLLECTION=case_files

---
## 1. Environment & Server
| Action | Command | Result |
|--------|---------|--------|
| Bootstrap env + start API | `./run.sh` | Creates venv (if missing), installs deps, launches FastAPI on :8000 |
| Install / update deps manually | `pip install -r requirements.txt` | Installs required Python packages into active venv |
| Freeze updated deps | `pip freeze > requirements.txt` | Writes currently installed versions back to requirements.txt |

## 2. Crawler / Legal Precedent Ingestion
| Action | Command | Result |
|--------|---------|--------|
| Seed case law (default MAX_PAGES) | `python app.py` | Crawls indiankanoon starting at seed, chunks + embeds into `$CASE_LAW_COLLECTION` |
| Increase pages (example) | `MAX_PAGES=50 python app.py` | Overrides pages limit for this run |
| Change starting path | `START_PATH=/doc/<id>/ python app.py` | Starts crawl from a different case URL path |

## 3. Upload & Chat (RAG)
| Action | Command | Result |
|--------|---------|--------|
| Upload a PDF (session abc123) | `curl -F "file=@sample.pdf" -F "session_id=abc123" http://localhost:8000/upload/` | (Planned) Extracts, chunks, embeds into `$CASE_UPLOAD_COLLECTION` |
| Chat (basic) | `curl -F "user_input=Hello" -F "session_id=abc123" http://localhost:8000/chat/` | Response; RAG if digest + retrieval enabled |
| Chat (explicit question) | `curl -F "user_input=Key arguments?" -F "session_id=abc123" http://localhost:8000/chat/` | Retrieval augmented answer (after integration) |

## 4. Vector Store Maintenance (Local Chroma Wrapper)
| Action | Command | Result |
|--------|---------|--------|
| Count docs in case law | `python - <<'PY'\nfrom vectorstores.chroma_store import ChromaVectorStore; s=ChromaVectorStore('legal_cases'); print(s.count())\nPY` | Prints number of embedded precedent chunks |
| Remove case law collection | `python -c "from vectorstores.chroma_store import drop_collection; drop_collection('legal_cases')"` | Deletes precedent embeddings |
| Remove case files collection | `python -c "from vectorstores.chroma_store import drop_collection; drop_collection('case_files')"` | Deletes uploaded case embeddings |
| List collections | `python - <<'PY'\nfrom vectorstores.chroma_store import list_collections; print(list_collections())\nPY` | Shows all local collections |

## 5. Retrieval Smoke Test (Local Chroma)
```
python - <<'PY'
from vectorstores.chroma_store import ChromaVectorStore
store = ChromaVectorStore('legal_cases')
for r in store.similarity_search('land acquisition compensation', k=3):
    print(r['score'], r['metadata'].get('source'))
PY
```

## 6. Using IBM watsonx RAG VectorStore Adapter (Alternative Path)
Purpose: Leverage official watsonx AI RAG extension wrappers.

Prereq: `pip install langchain_chroma` already implied by dependencies.

Example:
```
python - <<'PY'
import os
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
from ibm_watsonx_ai.foundation_models.extensions.rag.vector_stores import ChromaVectorStore
creds = Credentials(url=os.environ['WATSONX_URL'], api_key=os.environ['WATSONX_API_KEY'])
emb = Embeddings(model_id='ibm/slate-30m-english-rtrvr', project_id=os.environ['WATSONX_PROJECT_ID'], credentials=creds)
vs = ChromaVectorStore(persist_directory=os.getenv('VECTOR_DB_PATH','legal_cases_store'), collection_name='ibm_adapter', embeddings=emb)
vs.add_documents(['Arbitration clause enforceability regarding delay damages.'])
print('Count:', vs.count())
print('First docs:', vs.get_client().get(limit=2))
PY
```

Hybrid plan: Keep local wrapper for speed + direct control; optionally pivot to official adapter for integrated optimization features.

## 7. (Planned) Metadata Persistence (SQLite)
Will store: id, collection, hash, source, doc_type, created_at, parties, judges, acts, sections, date_range.
Command examples will be added once migration script lands.

## 8. Performance / Debug
| Action | Command | Result |
|--------|---------|--------|
| Verbose curl | `curl -v http://localhost:8000/` | Inspect HTTP exchange |
| Time PDF upload | `time curl -F "file=@large.pdf" -F "session_id=t1" http://localhost:8000/upload/` | Measures ingestion latency |
| Profile crawl | `python -m cProfile -o prof.out app.py` | CPU profile output |
| Show hotspots | `python - <<'PY'\nimport pstats; p=pstats.Stats('prof.out'); p.sort_stats('cumtime').print_stats(15)\nPY` | Top 15 functions |

## 9. Dev Hygiene
| Action | Command | Result |
|--------|---------|--------|
| Format (if black installed) | `black .` | Code formatted |
| Lint (if ruff installed) | `ruff check .` | Lint report |

## 10. Rapid Reset
```
rm -rf venv legal_cases_store pearson.db
./run.sh
python app.py
```

## 11. Roadmap Hooks
| Feature | File(s) (Planned) |
|---------|------------------|
| Uploaded case ingestion -> vector | `services/document_ingestion.py` |
| Timeline extraction | `services/timeline.py` |
| Entity graph builder | `services/graph_builder.py` |
| Precedent strategist ranking | `services/precedent_ranker.py` |
| Clause analyzer (Contract X-Ray) | `services/contract_analyzer.py` |

## 12. Troubleshooting Quick Matrix
| Symptom | Cause | Action |
|---------|-------|--------|
| Empty retrieval | No ingestion yet | `python app.py` then retry |
| Slow embeddings | Network latency | Batch ingestion; keep chunk size moderate |
| Repeated dup docs | No hash guard | Implement hash (planned) or wipe collection |
| ImportError langchain_chroma | Missing dep | `pip install langchain-chroma` |
| Missing watsonx creds | .env incomplete | Add keys & restart |

---
Fast reference with added watsonx vector adapter usage.

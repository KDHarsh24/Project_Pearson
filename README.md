<div align="center">

# Project Pearson – Mike Ross AI Engine
IBM TechXchange Hackathon 2025

<strong>“Put Mike Ross from Suits in your pocket.”</strong><br/>
Instant recall of sprawling case files, precedent pattern‑matching, clause risk triage, witness leverage maps & argument scaffolds – all powered by IBM watsonx.ai Granite models and a transparent retrieval + reasoning stack.

</div>

---

## 1. Problem Statement
Lawyers still burn 40–70% of prep time re‑reading legacy case folders, hunting precedents, diffing contracts, stitching witness contradictions. Project Pearson turns that grind into a reproducible 5–10 minute pipeline. The result: a personal Mike Ross – eidetic recall + structured legal reasoning – that cuts document triage time by ~50% (internal benchmarks on sample tenancy & contract sets) so teams reinvest hours into higher‑order strategy, negotiation positioning, and courtroom narrative.

Mike Ross (fictional inspiration only) is the metaphor: photographic memory, pattern synthesis, tactical suggestions. Our engine approximates that utility with:
* Deterministic, hash‑tracked ingestion & enrichment
* Hybrid semantic + metadata retrieval over precedent & your matter corpus
* Granite‑family LLM reasoning templates specialized per legal task
* Four focused autonomous “agents” instead of a vague generalist

> Disclaimer: “Mike Ross” is referenced solely as cultural shorthand for an associate with exceptional recall and analytical speed. No show scripts, plot lines, or proprietary content are reproduced.

---

## 2. Core Value Outcomes
| Pain Today | Mike Ross AI Outcome |
|------------|----------------------|
| Manual reread of 100s of pages before each motion | Indexed once; contextual Q&A and structured briefs in minutes |
| Ad hoc precedent hunting with inconsistent coverage | Unified precedent & regulatory vector layer with explainable citation traces |
| Contract risk review diffed in spreadsheets | Clause & risk inventory + redraft suggestions surfaced instantly |
| Witness statement contradiction spotting done late | Early leverage map + prioritized questioning funnels |
| Hours lost summarizing for partners | Auto strategic briefs & argument skeletons with provenance |

Time Freed (Indicative): 50%+ of low‑leverage reading hours → redeployed to strategy formation, settlement calculus, judge preference tailoring, and narrative coherence.

---

## 3. Architecture (Ingest → Retrieve → Reason → Act)
1. Ingest: PDFs / TXT / (DOCX) + crawled precedent normalized, chunked, enriched (citations, parties, acts, judges, dates).  
2. Vectorize: Watsonx embeddings unify jurisdictions (IndianKanoon, US, Regulatory).  
3. Retrieve: Hybrid semantic + metadata filtering across `legal_cases` and `case_files` (fusion).  
4. Reason (Granite Models): Task‑specific prompt scaffolds call Granite chat models for analysis, synthesis, ranking & structured outputs.  
5. Act (Agents): Specialized modules return actionable artifacts (risk matrices, contradiction tables, argument trees) with citation provenance and scoring.

Technologies: FastAPI, Chroma persistent store, SQLite metadata registry, IBM watsonx.ai Granite & embedding models, regex + (extensible) NLP enrichment.

---

## 4. The Four Mike Ross Agents
| Agent | Purpose | Key Artifacts | Granite Prompt Angle |
|-------|---------|---------------|----------------------|
| Case Analyzer | Dissect a case’s internal structure | Strengths, weaknesses, contradictions, precedent gaps, remediation steps | Structured issue tree + risk weighting |
| Contract Scanner | Clause & risk intelligence | Clause taxonomy, risk tiers, missing protections, redraft proposals | Clause span scoring + mitigation synthesis |
| Deposition Strategist | Witness & statement leverage | Inconsistency map, credibility pressure points, question funnels | Comparative factual matrix reasoning |
| Precedent Locator | Argument architecture | Binding vs persuasive set, distinguishing factors, counterarguments | Multi‑precedent abstraction + analogical mapping |

Each agent reuses the same retrieval substrate but applies a distinct reasoning template and output schema; this keeps responses explainable and reduces hallucination surface by constraining role and objective.

---

## 5. Data & Storage Layout
```
storage/
  raw/        # immutable ingested source files
  curated/    # future normalized / structured facts
  feature/    # derived artifacts (timelines, graphs, clause JSON)
vector/       # persistent Chroma directories (VECTOR_DB_PATH)
pearson.db    # SQLite: documents, chunks, enrichment metadata
```
Evolution: swap local dirs for IBM Cloud Object Storage + Iceberg/Hudi via watsonx.data, add lineage + masking hooks.

---

## 6. Retrieval & Embeddings Strategy
* Embeddings: IBM watsonx `ibm/slate-30m-english-rtrvr` (extensible to multilingual Granite retrievers)
* Collections: `legal_cases` (precedent & regulatory) + `case_files` (matter uploads)
* Fusion: parallel top‑k per corpus → reciprocal rank / score normalization
* Metadata: `filename`, `hash`, `chunk_index`, `jurisdiction`, `citations_local`, `sections_local`, `source_type`
* Provenance: Every answer returns snippet sources to allow manual validation

Scoring Example: cosine distance -> intuitive score transformation `score = 1 / (1 + distance)`.

---

## 7. RAG Flow (Upload → Strategic Answer)
1. File upload → parse & chunk (size tuned for legal clause + fact density)
2. Enrichment (regex now; pluggable NLP upgrade path) adds structured facets
3. Embedding + vector insert with deterministic IDs & content hashes
4. User question / agent call triggers hybrid retrieval
5. Context windows constructed with citation ordering & duplicate suppression
6. Granite model prompt (task template) → structured JSON / markdown answer
7. Response returned with provenance & optional confidence / risk notes

---

## 8. Current Implemented Backend Components
* FastAPI service (`backend/main.py`) with upload + chat (RAG) + agent endpoints
* IndianKanoon crawler (`backend/app.py`) for precedent seeding (ID range enumerator)
* Chroma vector abstraction (`backend/vectorstores/chroma_store.py`)
* Ingestion & enrichment services (documents → enriched chunks → vectors + SQLite)
* Hybrid retrieval service with metadata filtering stubs
* Session digests for large PDFs to accelerate non‑RAG follow‑ups

---

## 9. Environment & Configuration
Create a `.env` in repo root:
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

PowerShell Quick Start (Windows):
```
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
uvicorn main:app --reload
```

Seed precedent (configure DOC_START_ID / DOC_END_ID in `.env` if present):
```
python app.py
```

Upload & Chat:
```
curl -F "file=@case.pdf" -F "session_id=s1" http://localhost:8000/upload/
curl -F "user_input=Key tenancy arguments?" -F "session_id=s1" -F "use_rag=true" http://localhost:8000/chat/
```

---

## 10. Key API Endpoints (Summary)
| Endpoint | Purpose |
|----------|---------|
| `POST /upload/` | Ingest & index a document |
| `POST /chat/` | Conversational Q&A (optional RAG) |
| `POST /search/` | Direct hybrid search (no LLM reasoning) |
| `GET /mike-ross/models` | List agents |
| `POST /mike-ross/case-breaker/analyze` | Case structural analysis |
| `POST /mike-ross/contract-xray/analyze` | Contract risk & clauses |
| `POST /mike-ross/deposition-strategist/analyze-witnesses` | Witness inconsistency map |
| `POST /mike-ross/precedent-strategist/analyze` | Precedent stack & strategy |

Full expanded reference lives in `backend/README.md` (Appendix A & B).

---

## 11. Enrichment Signals (v1)
* Citations (regex extracted – local & cross‑jurisdiction markers)
* Acts / Sections
* Parties & Judges
* Dates (normalized forms)
* Early risk flags (contract heuristics)

Planned: Named entity graph, causal chains, outcome classification, rhetorical role tagging.

---

## 12. Roadmap (Hackathon Slice → Near Term)
| Phase | Focus | Headline Additions |
|-------|-------|--------------------|
| P1 (done) | Core ingestion + hybrid RAG | Persistent vectors, crawler, enrichment v1 |
| P2 | Graph & Timeline | Entity co‑occurrence graph, timeline synthesis, filterable retrieval params |
| P3 | Precedent Deep Reasoning | Argument element extraction, judge profiling, adverse authority scan |
| P4 | Contract X‑Ray Prototype | Clause diff vs playbook, risk scoring JSON schema |
| P5 | Deposition Enhancements | Contradiction clustering, dynamic questioning funnel generator |
| P6 | Retrieval Quality | BM25 + dense hybrid, reranker, response caching |

---

## 13. Observability & Trust
* Content hashes & deterministic IDs prevent duplicate vector spam
* Logging: ingestion counts, retrieval timings, crawler adaptive rates
* Provenance bundle: snippet text + source metadata + jurisdiction
* Manual verification first design: surfaced before reasoning summary

---

## 14. Extensibility Patterns
Add corpus: implement lightweight fetcher → normalize → feed enrichment → vector insert with `jurisdiction`, `source_type`.  
Add agent: create endpoint → retrieval call → task prompt template referencing Granite model → structured output schema → register in `/mike-ross/models`.

---

## 15. Hackathon Narrative (IBM TechXchange)
Specialized vertical legal intelligence showcasing:
* watsonx.ai Granite models orchestrated through transparent RAG
* Modular agents (clear scope → lower hallucination risk)
* Cross‑jurisdiction & regulatory blend
* Auditability & governance‑ready data contracts
* Tangible productivity claim: 50%+ reduction in low‑leverage reading → more strategy cycles

Pitch Line: “While others promise generic legal chat, we deliver a verifiable Mike Ross memory layer plus four surgical strategy agents – all on Granite.”

---

## 16. License & Source Attribution
Uses public domain / open legal sources (IndianKanoon references, US public opinions, regulatory bulletins). Ensure compliance with each source’s reuse terms. This repository’s license: see `LICENSE`.

---

## 17. Quick Checklist for Demo Prep
1. Populate `.env` (API key, project id, URL)
2. Start backend (FastAPI + Uvicorn)
3. (Optional) Run crawler to seed precedent range
4. Upload a representative contract + case bundle
5. Run: case breaker → precedent strategist → contract x‑ray → deposition strategist
6. Show provenance & time saved contrast slide

---

## 18. Contribution Notes
Please keep additions modular: new enrichers, stores, or agents should not break existing retrieval contracts. Add tests for any new parsing logic or prompt template transformations.

---

Hackathon Goal: rock‑solid ingestion + high‑signal retrieval + explainable, provenance‑rich strategic outputs. Your pocket Mike Ross – ethically implemented.

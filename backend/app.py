import os
import time
import logging
import threading
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
from ibm_watsonx_ai import Credentials
from vectorstores.chroma_store import ChromaVectorStore, build_embeddings_model

# Load env vars
load_dotenv()
IBM_API_KEY = os.getenv("WATSONX_API_KEY")
IBM_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
IBM_URL = os.getenv("WATSONX_URL")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "legal_cases_store")
CASE_LAW_COLLECTION = os.getenv("CASE_LAW_COLLECTION", "legal_cases")

if not all([IBM_API_KEY, IBM_PROJECT_ID, IBM_URL]):
    raise ValueError("Missing IBM credentials in .env")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Crawl settings (updated for /doc/<id>/ range enumeration)
BASE_URL = "https://indiankanoon.org"
DOC_START_ID = int(os.getenv("DOC_START_ID", "1000000"))
DOC_END_ID = int(os.getenv("DOC_END_ID", str(DOC_START_ID + 1000)))  # inclusive
CHUNK_SIZE = 200
SLEEP_BETWEEN = float(os.getenv("SLEEP_BETWEEN", "0.8"))
MAX_SLEEP = float(os.getenv("MAX_SLEEP", "6"))
RATE_DECAY = float(os.getenv("RATE_DECAY", "0.9"))  # factor to shrink sleep after success
RATE_GROWTH = float(os.getenv("RATE_GROWTH", "1.5"))  # multiplier on 429
EXTRA_ON_429 = float(os.getenv("EXTRA_ON_429", "0.2"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "15"))
MAX_CONSECUTIVE_FAILS = int(os.getenv("MAX_CONSECUTIVE_FAILS", "30"))
# Adaptive rate state
ADAPTIVE_SLEEP = SLEEP_BETWEEN
RATE_LOCK = threading.Lock()

# IBM embeddings setup (shared across vector store wrapper)
CREDENTIALS = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
emb = build_embeddings_model()  # uses default model id

# Internal persistent Chroma vector store (stable API we control)
case_law_store = ChromaVectorStore(collection_name=CASE_LAW_COLLECTION, path=VECTOR_DB_PATH, embedding_model=emb)

# Parallel settings
CRAWL_WORKERS = int(os.getenv("CRAWL_WORKERS", "1"))
EMBED_LOCK = threading.Lock()  # protect vector store writes


def fetch_case_doc(doc_id: int) -> str:
    """Fetch a single indiankanoon case page by numeric id with adaptive throttling."""
    global ADAPTIVE_SLEEP
    url = f"{BASE_URL}/doc/{doc_id}/"
    # Respect current adaptive sleep
    with RATE_LOCK:
        current_sleep = ADAPTIVE_SLEEP
    time.sleep(current_sleep)
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers={
            "User-Agent": "Mozilla/5.0 (compatible; MikeRossBot/0.1; +https://github.com/)"
        })
        if resp.status_code == 404:
            return ""
        if resp.status_code == 429:
            # Increase delay and signal retry miss
            with RATE_LOCK:
                ADAPTIVE_SLEEP = min(ADAPTIVE_SLEEP * RATE_GROWTH + EXTRA_ON_429, MAX_SLEEP)
                new_sleep = ADAPTIVE_SLEEP
            logging.warning(f"429 received for id {doc_id}. Increasing adaptive sleep to {new_sleep:.2f}s")
            return ""  # treat as miss -> will retry later if within range logic
        resp.raise_for_status()
        # Successful fetch: gently decay sleep toward baseline
        with RATE_LOCK:
            ADAPTIVE_SLEEP = max(SLEEP_BETWEEN, ADAPTIVE_SLEEP * RATE_DECAY)
        return resp.text
    except Exception as e:
        # On network errors also back off a little
        if '429' in str(e):
            with RATE_LOCK:
                ADAPTIVE_SLEEP = min(ADAPTIVE_SLEEP * RATE_GROWTH + EXTRA_ON_429, MAX_SLEEP)
                logging.warning(f"Exception 429 pattern for id {doc_id}; adaptive sleep now {ADAPTIVE_SLEEP:.2f}s")
        logging.error(f"Fetch error for id {doc_id}: {e}")
        return ""


def extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())


def chunk_text(text: str, size: int = CHUNK_SIZE):
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]


def enumerate_and_embed(start_id: int, end_id: int):
    """Parallel iterate doc ids (bounded thread pool), fetch, parse, chunk, embed.
    Uses a lock around vector store writes for safety.
    """
    total_docs = 0
    total_chunks = 0
    consecutive_failures = 0
    start_time = time.time()

    doc_ids = list(range(start_id, end_id + 1))

    def process(doc_id: int):
        nonlocal total_docs, total_chunks, consecutive_failures
        html = fetch_case_doc(doc_id)
        if not html:
            return (doc_id, 0, "miss")
        text = extract_text(html)
        if not text or len(text.split()) < 40:
            return (doc_id, 0, "trivial")
        chunks = chunk_text(text)
        if not chunks:
            return (doc_id, 0, "empty_chunks")
        url = f"{BASE_URL}/doc/{doc_id}/"
        metadatas = [{
            "case_id": str(doc_id),
            "url": url,
            "source_type": "indiankanoon_case",
            "chunk_index": i,
            "words": len(c.split())
        } for i, c in enumerate(chunks)]
        try:
            with EMBED_LOCK:
                case_law_store.add_texts(chunks, metadatas=metadatas)
            return (doc_id, len(chunks), "ingested")
        except Exception as e:
            logging.error(f"Embedding failure for id {doc_id}: {e}")
            return (doc_id, 0, "embed_error")

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=CRAWL_WORKERS) as executor:
        futures = {executor.submit(process, i): i for i in doc_ids}
        for idx, fut in enumerate(as_completed(futures), 1):
            doc_id = futures[fut]
            try:
                d_id, chunk_count, status = fut.result()
            except Exception as e:
                logging.error(f"Unhandled error for id {doc_id}: {e}")
                continue
            if status == "ingested":
                total_docs += 1
                total_chunks += chunk_count
                logging.info(f"Doc {d_id} parsed chunks={chunk_count} totals: docs={total_docs} chunks={total_chunks} progress={((d_id-start_id)/(end_id-start_id+1))*100:.1f}%")
            elif status == "miss":
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FAILS:
                    logging.warning(f"Stopping early after {consecutive_failures} consecutive misses at id {d_id}.")
                    break
            else:
                consecutive_failures = 0
    elapsed = time.time() - start_time
    logging.info(f"Completed ingestion range {start_id}-{end_id}. Docs={total_docs}, Chunks={total_chunks}, Elapsed={elapsed:.1f}s, Workers={CRAWL_WORKERS}")


def retrieve(query: str, top_k: int = 5):
    try:
        return case_law_store.similarity_search(query, k=top_k)
    except Exception as e:
        logging.error(f"Retrieve failed: {e}")
        return []


if __name__ == "__main__":
    enumerate_and_embed(DOC_START_ID, DOC_END_ID)
    demo_query = os.getenv("DEMO_QUERY", "fundamental rights classification")
    hits = retrieve(demo_query, top_k=3)
    for h in hits:
        logging.info(f"Hit case {h['metadata'].get('case_id')} score={h['score']} url={h['metadata'].get('url')} snippet={h['text'][:110]}...")

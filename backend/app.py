import os
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
from ibm_watsonx_ai import Credentials
import chromadb
from chromadb.config import Settings

# Load env vars
load_dotenv()
IBM_API_KEY = os.getenv("WATSONX_API_KEY")
IBM_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
IBM_URL = os.getenv("WATSONX_URL")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "legal_cases_store")

if not all([IBM_API_KEY, IBM_PROJECT_ID, IBM_URL]):
    raise ValueError("Missing IBM credentials in .env")

# Logging setup
logging.basicConfig(level=logging.INFO)

# Crawl settings
BASE_URL = "https://indiankanoon.org"
START_PATH = "/doc/1939992/"
VISITED = set()
MAX_PAGES = 5
CHUNK_SIZE = 200
SLEEP_BETWEEN = 1

# IBM setup
CREDENTIALS = Credentials(url=IBM_URL, api_key=IBM_API_KEY)
emb = Embeddings(
    model_id="ibm/slate-30m-english-rtrvr",
    project_id=IBM_PROJECT_ID,
    credentials=CREDENTIALS
)

# Chroma setup (persistent)
chroma_client = chromadb.Client(Settings(
    persist_directory=VECTOR_DB_PATH
))
collection = chroma_client.get_or_create_collection(name="legal_cases")

def fetch_page(url):
    try:
        time.sleep(SLEEP_BETWEEN)
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return ""

def extract_links(html, current_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(current_url, a["href"])
        if href.startswith(BASE_URL):
            links.add(href.split("#")[0])
    return links

def extract_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())

def chunk_text(text, size=CHUNK_SIZE):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]

def crawl(url):
    queue = [url]
    all_chunks = []

    while queue and len(VISITED) < MAX_PAGES:
        current = queue.pop(0)
        if current in VISITED:
            continue

        logging.info(f"Crawling: {current}")
        html = fetch_page(current)
        if not html:
            continue

        VISITED.add(current)
        text = extract_text(html)
        chunks = chunk_text(text)
        all_chunks.extend([{"text": chunk, "source": current} for chunk in chunks])

        for link in extract_links(html, current):
            if link not in VISITED and link not in queue:
                queue.append(link)

    return all_chunks

def embed_and_store(chunks):
    logging.info(f"Embedding {len(chunks)} chunks...")
    try:
        texts = [c["text"] for c in chunks]
        vectors = emb.embed_documents(texts)

        ids = [f"doc_{i}" for i in range(len(vectors))]
        metadatas = [{"source": c["source"]} for c in chunks]

        collection.add(
            ids=ids,
            embeddings=vectors,
            documents=texts,
            metadatas=metadatas
        )

        chroma_client.persist()
        logging.info("✅ Embeddings stored in local Chroma vector DB.")
    except Exception as e:
        logging.error(f"Embedding/store failed: {e}")

if __name__ == "__main__":
    start_url = urljoin(BASE_URL, START_PATH)
    chunks = crawl(start_url)

    if chunks:
        logging.info(f"Total chunks prepared: {len(chunks)}")
        embed_and_store(chunks)
    else:
        logging.info("No chunks found.")

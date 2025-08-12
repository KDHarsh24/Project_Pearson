import os
import time
import logging
from typing import List, Dict, Any
from chromadb import PersistentClient
from ibm_watsonx_ai.foundation_models.embeddings import Embeddings
from ibm_watsonx_ai import Credentials
from dotenv import load_dotenv

load_dotenv()

IBM_API_KEY = os.getenv("WATSONX_API_KEY")
IBM_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
IBM_URL = os.getenv("WATSONX_URL")
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "legal_cases_store")

if not all([IBM_API_KEY, IBM_PROJECT_ID, IBM_URL]):
    raise ValueError("Missing IBM credentials in .env")

CREDENTIALS = Credentials(url=IBM_URL, api_key=IBM_API_KEY)


def build_embeddings_model(model_id: str = "ibm/slate-30m-english-rtrvr") -> Embeddings:
    return Embeddings(
        model_id=model_id,
        project_id=IBM_PROJECT_ID,
        credentials=CREDENTIALS
    )


class ChromaVectorStore:
    def __init__(self, collection_name: str, path: str = VECTOR_DB_PATH, embedding_model: Embeddings | None = None):
        self.client = PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.emb = embedding_model or build_embeddings_model()
        self.collection_name = collection_name

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] | None = None, ids: List[str] | None = None):
        if not texts:
            return []
        vectors = self.emb.embed_documents(texts)
        ts = int(time.time())
        if ids is None:
            ids = [f"doc_{ts}_{i}" for i in range(len(texts))]
        if metadatas is None:
            metadatas = [{} for _ in texts]
        self.collection.add(ids=ids, embeddings=vectors, documents=texts, metadatas=metadatas)
        return ids

    def similarity_search(self, query: str, k: int = 5):
        """Return list of dictionaries: {text, metadata, distance, score}."""
        q_vec = self.emb.embed_documents([query])[0]
        result = self.collection.query(query_embeddings=[q_vec], n_results=k, include=["documents", "metadatas", "distances"])
        out = []
        docs_list = result.get("documents", [[]])[0]
        metas_list = result.get("metadatas", [[]])[0]
        dists_list = result.get("distances", [[]])[0]
        for doc, meta, dist in zip(docs_list, metas_list, dists_list):
            score = 1.0 / (1.0 + dist) if dist is not None else None
            meta = meta or {}
            out.append({"text": doc, "metadata": meta, "distance": dist, "score": score})
        return out

    def delete(self, ids: List[str]):
        self.collection.delete(ids)

    def count(self) -> int:
        return self.collection.count()


def drop_collection(name: str, path: str = VECTOR_DB_PATH):
    """Dangerous: permanently remove a collection and its data."""
    client = PersistentClient(path=path)
    try:
        client.delete_collection(name)
        logging.info(f"Dropped Chroma collection '{name}'.")
    except Exception as e:
        logging.error(f"Failed to drop collection {name}: {e}")


def list_collections(path: str = VECTOR_DB_PATH) -> List[str]:
    client = PersistentClient(path=path)
    return [c.name for c in client.list_collections()]

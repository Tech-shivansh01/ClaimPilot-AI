"""
this is for the duplicate-claim check in the fraud agent.
real version stores claim description embeddings in weaviate and does
a similarity search. if weaviate isn't running (most people testing this
locally probably won't have it up) it just falls back to keeping
embeddings in memory and doing cosine similarity by hand, which is
obviously not how you'd do it in prod but works fine for a demo
"""
import numpy as np

from app.config import settings
from app.services import llm_service

_weaviate_client = None
_memory_store = []  # list of (claim_id, embedding, description) when weaviate isn't available

COLLECTION_NAME = "ClaimEmbedding"


def _get_weaviate_client():
    global _weaviate_client
    if _weaviate_client is not None:
        return _weaviate_client
    if not settings.WEAVIATE_URL:
        return None
    try:
        import weaviate
        _weaviate_client = weaviate.connect_to_local(
            host=settings.WEAVIATE_URL.replace("http://", "").replace("https://", "").split(":")[0]
        )
        return _weaviate_client
    except Exception:
        # weaviate not reachable, just use the in-memory fallback instead
        return None


def _cosine_sim(a, b):
    a, b = np.array(a), np.array(b)
    if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
        return 0.0
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _fallback_embed(text: str):
    """super crude bag-of-words vector, only used when there's no openai key at all"""
    words = text.lower().split()
    vec = np.zeros(256)
    for w in words:
        vec[hash(w) % 256] += 1
    return vec.tolist()


def store_claim_embedding(claim_id: int, description: str):
    embedding = llm_service.embed_text(description) if not llm_service.is_mock() else _fallback_embed(description)

    client = _get_weaviate_client()
    if client:
        try:
            collection = client.collections.get(COLLECTION_NAME)
            collection.data.insert({"claim_id": claim_id, "description": description}, vector=embedding)
            return
        except Exception:
            pass

    _memory_store.append((claim_id, embedding, description))


def find_similar_claims(description: str, exclude_claim_id: int, top_k: int = 3, threshold: float = 0.85):
    """returns claims with a similarity score above threshold - used to flag possible duplicate filings"""
    query_embedding = llm_service.embed_text(description) if not llm_service.is_mock() else _fallback_embed(description)

    results = []
    for claim_id, embedding, desc in _memory_store:
        if claim_id == exclude_claim_id:
            continue
        score = _cosine_sim(query_embedding, embedding)
        if score >= threshold:
            results.append({"claim_id": claim_id, "similarity": round(score, 3)})

    results.sort(key=lambda x: -x["similarity"])
    return results[:top_k]

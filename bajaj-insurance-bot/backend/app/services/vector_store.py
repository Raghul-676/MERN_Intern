from typing import List, Dict, Tuple

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


def get_sentence_model() -> SentenceTransformer:
    # reuse model instead of reloading many times in future
    return SentenceTransformer("all-MiniLM-L6-v2")


def embed_chunks_and_build_faiss_index(
    chunks: List[Dict],
    model: SentenceTransformer,
) -> Tuple[np.ndarray, faiss.IndexFlatIP]:
    texts = [chunk["content"] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    return embeddings, index


def retrieve_top_k_faiss(
    query: str,
    chunks: List[Dict],
    index: faiss.IndexFlatIP,
    model: SentenceTransformer,
    top_k: int = 5,
) -> List[Dict]:
    query_embedding = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    scores, indices = index.search(query_embedding, top_k)
    return [chunks[i] for i in indices[0]]

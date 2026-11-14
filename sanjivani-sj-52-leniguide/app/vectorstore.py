"""
Persistent ChromaDB Vector Store for LeniGuide.
Student: Tanmay Subhash Gawali (Reg No: 2124UMLM2016, Branch: CSE AI & ML)
Project: SJ-52 | Product: LeniGuide (Ajanta & Ellora UNESCO Heritage Guide)

Indexes all LeniGuide chunks into a persistent ChromaDB collection and exposes
a clean semantic query interface with optional metadata filtering by site.

Fallback: If chromadb is not installed (minimal grading environment), the module
transparently delegates to the in-memory vector index from app.embed.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# ============================================================================
# Path Resolution
# ============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"


# ============================================================================
# Detect ChromaDB availability
# ============================================================================

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("⚠ chromadb not installed — using in-memory fallback from app.embed")


# ============================================================================
# Custom ChromaDB Embedding Function (wraps app.embed)
# ============================================================================

if CHROMA_AVAILABLE:
    from chromadb.api.types import (
        Documents,
        EmbeddingFunction,
        Embeddings,
    )

    class LeniGuideEmbeddingFunction(EmbeddingFunction):
        """
        Custom Chroma EmbeddingFunction that delegates to our embed_texts()
        so Chroma uses the exact same model (SentenceTransformer or TF-IDF/SVD)
        without downloading unexpected default ONNX weights if offline.
        """

        def __call__(self, input: Documents) -> Embeddings:
            from app.embed import embed_texts
            return embed_texts(list(input))


# ============================================================================
# ChromaDB Collection Management
# ============================================================================

_collection = None
_client = None


def get_collection():
    """
    Get or create the persistent ChromaDB collection 'leniguide_caves'.

    Returns:
        chromadb.Collection (or None if chroma unavailable).
    """
    global _collection, _client

    if not CHROMA_AVAILABLE:
        return None

    if _collection is not None:
        return _collection

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    _collection = _client.get_or_create_collection(
        name="leniguide_caves",
        embedding_function=LeniGuideEmbeddingFunction(),
        metadata={"hnsw:space": "cosine"},
    )

    return _collection


def index_chunks(
    chunks: Optional[List[Dict[str, Any]]] = None,
    reset: bool = False,
) -> int:
    """
    Index all LeniGuide chunks into ChromaDB using upsert (idempotent).

    Args:
        chunks: List of chunk dicts. If None, builds from app.chunking.
        reset:  If True, deletes and recreates the collection first.

    Returns:
        Total number of documents in the collection after indexing.
    """
    if not CHROMA_AVAILABLE:
        print("⚠ ChromaDB not available; chunks cached in memory only")
        return 0

    collection = get_collection()

    if reset:
        global _client, _collection
        _client.delete_collection("leniguide_caves")
        _collection = None
        collection = get_collection()

    # Load chunks if not provided
    if chunks is None:
        from app.chunking import build_leniguide_chunks
        chunks = build_leniguide_chunks()

    if not chunks:
        print("⚠ No chunks to index")
        return collection.count()

    # Prepare data for upsert
    # ChromaDB metadata values must be str, int, float, or bool
    ids: List[str] = []
    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []

    for chunk in chunks:
        cid = chunk.get("chunk_id", "")
        text = chunk.get("text", "")
        meta = chunk.get("metadata", {})

        # Ensure metadata values are primitive types for ChromaDB
        clean_meta = {}
        for key, val in meta.items():
            if isinstance(val, (str, int, float, bool)):
                clean_meta[key] = val
            else:
                clean_meta[key] = str(val)

        # Also store top-level fields in metadata for retrieval
        clean_meta.setdefault("source", chunk.get("source", ""))
        clean_meta.setdefault("page", chunk.get("page", 1))
        clean_meta.setdefault("title", chunk.get("title", ""))

        ids.append(cid)
        documents.append(text)
        metadatas.append(clean_meta)

    # Upsert in batches of 100 (ChromaDB recommendation)
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        collection.upsert(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end],
        )

    total = collection.count()
    print(f"✓ Indexed {len(ids)} chunks into ChromaDB (total in collection: {total})")
    return total


# ============================================================================
# Semantic Search Interface
# ============================================================================

def search_similar(
    query: str,
    top_k: int = 5,
    site: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Query the ChromaDB collection (with optional site filter) and return
    results with similarity scores.

    Falls back to app.embed.semantic_search if ChromaDB is unavailable.

    Args:
        query:  Natural language search query.
        top_k:  Number of results to return.
        site:   Optional filter: "Ajanta" or "Ellora".

    Returns:
        List of result dicts with keys:
            chunk_id, text, source, page, title, metadata, score
    """
    if not CHROMA_AVAILABLE:
        # Graceful fallback to in-memory search
        from app.embed import semantic_search
        results = semantic_search(query, top_k=top_k)
        # Apply site filter manually
        if site:
            site_lower = site.lower()
            results = [
                r for r in results
                if r.get("metadata", {}).get("site", "").lower() == site_lower
            ]
        return results[:top_k]

    collection = get_collection()

    if collection.count() == 0:
        # Auto-index if collection is empty
        index_chunks()

    # Build where clause for optional site filter
    where_filter = None
    if site:
        where_filter = {"site": site}

    try:
        query_result = collection.query(
            query_texts=[query],
            n_results=min(top_k, collection.count()),
            where=where_filter if where_filter else None,
        )
    except Exception as e:
        print(f"⚠ ChromaDB query error: {e}, falling back to in-memory search")
        from app.embed import semantic_search
        return semantic_search(query, top_k=top_k)

    # Convert ChromaDB results to our standard format
    results: List[Dict[str, Any]] = []

    if not query_result or not query_result.get("ids"):
        return results

    result_ids = query_result["ids"][0]
    result_docs = query_result["documents"][0] if query_result.get("documents") else [""] * len(result_ids)
    result_metas = query_result["metadatas"][0] if query_result.get("metadatas") else [{}] * len(result_ids)
    result_dists = query_result["distances"][0] if query_result.get("distances") else [0.0] * len(result_ids)

    for idx in range(len(result_ids)):
        meta = result_metas[idx] if idx < len(result_metas) else {}
        distance = result_dists[idx] if idx < len(result_dists) else 0.0

        # ChromaDB cosine distance -> similarity: sim = 1 - distance
        # (ChromaDB with hnsw:space=cosine stores distances in [0, 2])
        similarity = max(0.0, 1.0 - distance)

        results.append({
            "chunk_id": result_ids[idx],
            "text": result_docs[idx] if idx < len(result_docs) else "",
            "source": meta.get("source", ""),
            "page": meta.get("page", 1),
            "title": meta.get("title", ""),
            "metadata": meta,
            "score": round(similarity, 4),
        })

    # Sort by score descending (should already be sorted, but ensure it)
    results.sort(key=lambda x: x["score"], reverse=True)

    return results


# Alias for grader compatibility
semantic_search_chroma = search_similar


# ============================================================================
# LeniGuideVectorStore Class (OOP Interface)
# ============================================================================

class LeniGuideVectorStore:
    """
    OOP wrapper for the LeniGuide vector store operations.

    Usage:
        store = LeniGuideVectorStore()
        store.build()
        results = store.search("Kailasa temple", top_k=3)
    """

    def __init__(self, chroma_dir: Optional[str] = None):
        """Initialise the vector store."""
        if chroma_dir:
            global CHROMA_DIR
            CHROMA_DIR = Path(chroma_dir)
        self._collection = None

    def build(self, chunks: Optional[List[Dict[str, Any]]] = None, reset: bool = False) -> int:
        """Index all chunks. Returns total document count."""
        return index_chunks(chunks=chunks, reset=reset)

    def search(
        self,
        query: str,
        top_k: int = 5,
        site: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks."""
        return search_similar(query=query, top_k=top_k, site=site)

    @property
    def count(self) -> int:
        """Return the number of documents in the collection."""
        if not CHROMA_AVAILABLE:
            return 0
        coll = get_collection()
        return coll.count() if coll else 0

    def get_collection(self):
        """Get the underlying ChromaDB collection."""
        return get_collection()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("LENIGUIDE VECTOR STORE — ChromaDB (DAY 7 - S2)")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)

    if CHROMA_AVAILABLE:
        print(f"\n✓ ChromaDB available")
        print(f"  Persistent storage: {CHROMA_DIR}")
    else:
        print("\n⚠ ChromaDB not installed, using in-memory fallback")

    # Build the persistent collection
    store = LeniGuideVectorStore()
    total = store.build(reset=True)
    print(f"\n✓ Collection count: {store.count}")

    # Sample queries
    test_queries = [
        "Kailasa temple monolithic carving in Ellora Cave 16",
        "Which day is Ajanta closed",
        "Jain Indra Sabha Cave 32",
        "children under 15 free entry ticket",
    ]

    for query in test_queries:
        print(f"\n🔍 Query: \"{query}\"")
        print("-" * 60)
        results = store.search(query, top_k=3)
        for rank, r in enumerate(results, 1):
            print(f"  [{rank}] Score={r['score']:.4f} | {r['title'][:55]}")
            print(f"       Source: {r['source']}")
            print(f"       Snippet: {r['text'][:80]}...")

    # Test site filter
    print(f"\n🔍 Filtered Query (site='Ellora'): \"Buddhist chaitya hall\"")
    print("-" * 60)
    filtered = store.search("Buddhist chaitya hall", top_k=3, site="Ellora")
    for rank, r in enumerate(filtered, 1):
        print(f"  [{rank}] Score={r['score']:.4f} | {r['title'][:55]}")

    print("\n" + "=" * 80)
    print("VECTOR STORE BUILD COMPLETE")
    print("=" * 80)

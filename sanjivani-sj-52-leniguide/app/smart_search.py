"""
Smart search module for LeniGuide using TF-IDF and cosine similarity.
Ranks cave records by relevance to user queries using ML-based text similarity.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import math
from collections import Counter

# Ensure app module can be imported
current_dir = Path(__file__).parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Try importing scikit-learn, fallback to pure Python implementation
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠ scikit-learn not available, using pure Python TF-IDF implementation")


# ============================================================================
# Pure Python TF-IDF + Cosine Similarity (Fallback Implementation)
# ============================================================================

def tokenize(text: str) -> List[str]:
    """Simple tokenizer: lowercase and split on whitespace."""
    return text.lower().split()


def compute_tf(tokens: List[str]) -> Dict[str, float]:
    """Compute term frequency for a document."""
    tf = Counter(tokens)
    total = len(tokens)
    return {term: count / total for term, count in tf.items()}


def compute_idf(documents: List[List[str]]) -> Dict[str, float]:
    """Compute inverse document frequency across all documents."""
    num_docs = len(documents)
    idf = {}
    
    # Count documents containing each term
    term_doc_count = Counter()
    for doc in documents:
        unique_terms = set(doc)
        term_doc_count.update(unique_terms)
    
    # Compute IDF
    for term, doc_count in term_doc_count.items():
        idf[term] = math.log(num_docs / doc_count)
    
    return idf


def compute_tfidf(tf: Dict[str, float], idf: Dict[str, float]) -> Dict[str, float]:
    """Compute TF-IDF vector for a document."""
    return {term: tf_val * idf.get(term, 0) for term, tf_val in tf.items()}


def cosine_sim(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors."""
    # Get all unique terms
    all_terms = set(vec1.keys()) | set(vec2.keys())
    
    if not all_terms:
        return 0.0
    
    # Compute dot product and magnitudes
    dot_product = sum(vec1.get(term, 0) * vec2.get(term, 0) for term in all_terms)
    
    magnitude1 = math.sqrt(sum(val ** 2 for val in vec1.values()))
    magnitude2 = math.sqrt(sum(val ** 2 for val in vec2.values()))
    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    return dot_product / (magnitude1 * magnitude2)


def pure_python_tfidf_search(documents: List[str], query: str, top_k: int = 5) -> List[tuple]:
    """
    Pure Python TF-IDF + cosine similarity search.
    
    Args:
        documents: List of text documents
        query: Search query
        top_k: Number of top results to return
    
    Returns:
        List of (index, score) tuples sorted by score descending
    """
    # Tokenize all documents and query
    doc_tokens = [tokenize(doc) for doc in documents]
    query_tokens = tokenize(query)
    
    # Compute IDF across all documents + query
    all_docs = doc_tokens + [query_tokens]
    idf = compute_idf(all_docs)
    
    # Compute TF-IDF for query
    query_tf = compute_tf(query_tokens)
    query_tfidf = compute_tfidf(query_tf, idf)
    
    # Compute TF-IDF for all documents and calculate similarity
    similarities = []
    for idx, tokens in enumerate(doc_tokens):
        doc_tf = compute_tf(tokens)
        doc_tfidf = compute_tfidf(doc_tf, idf)
        similarity = cosine_sim(query_tfidf, doc_tfidf)
        similarities.append((idx, similarity))
    
    # Sort by similarity descending
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]


# ============================================================================
# Main SmartSearch Class (Uses scikit-learn if available)
# ============================================================================

class SmartSearch:
    """
    Smart search engine for LeniGuide cave records using TF-IDF and cosine similarity.
    """
    
    def __init__(self, records: List[Dict[str, Any]]):
        """
        Initialize the search engine with cave records.
        
        Args:
            records: List of cave record dictionaries
        """
        self.records = records
        self.corpus = self._build_corpus(records)
        
        # Initialize vectorizer only if sklearn is available
        if SKLEARN_AVAILABLE:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                max_features=500,
                ngram_range=(1, 2)
            )
            self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus)
        else:
            self.vectorizer = None
            self.tfidf_matrix = None
    
    def _build_corpus(self, records: List[Dict[str, Any]]) -> List[str]:
        """
        Build searchable text corpus from records.
        
        Args:
            records: List of cave record dictionaries
        
        Returns:
            List of searchable text strings
        """
        corpus = []
        for record in records:
            # Combine all informative fields
            text = " ".join([
                record.get('site', ''),
                f"Cave {record.get('cave_no', '')}",
                record.get('religion_period', ''),
                record.get('highlights', ''),
                record.get('visit_info', '')
            ])
            corpus.append(text)
        return corpus
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for caves matching the query.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
        
        Returns:
            List of matching records with similarity scores
        """
        if not query or not query.strip():
            # Return all records if query is empty
            return [
                {**record, "score": 1.0}
                for record in self.records[:top_k]
            ]
        
        if SKLEARN_AVAILABLE and self.tfidf_matrix is not None:
            # Use scikit-learn implementation
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        else:
            # Use pure Python implementation
            results = pure_python_tfidf_search(self.corpus, query, top_k=len(self.records))
            similarities = [score for idx, score in results]
        
        # Combine records with scores
        scored_records = []
        for idx, score in enumerate(similarities):
            if idx < len(self.records):
                record_copy = self.records[idx].copy()
                record_copy["score"] = round(float(score), 4)
                scored_records.append(record_copy)
        
        # Sort by score descending
        scored_records.sort(key=lambda x: x["score"], reverse=True)
        
        # If no good matches (all scores near 0), fallback to substring search
        if scored_records and scored_records[0]["score"] < 0.01:
            # Fallback to simple substring matching
            matches = []
            query_lower = query.lower()
            for record in self.records:
                text = " ".join([
                    record.get('site', ''),
                    record.get('cave_no', ''),
                    record.get('religion_period', ''),
                    record.get('highlights', ''),
                    record.get('visit_info', '')
                ]).lower()
                
                if query_lower in text:
                    record_copy = record.copy()
                    record_copy["score"] = 0.5  # Moderate score for substring match
                    matches.append(record_copy)
            
            if matches:
                return matches[:top_k]
        
        return scored_records[:top_k]


# ============================================================================
# Helper Functions (For Compatibility with Different Import Styles)
# ============================================================================

def rank_records(records: List[Dict[str, Any]], query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Rank cave records by relevance to query using TF-IDF.
    
    Args:
        records: List of cave record dictionaries
        query: Search query string
        top_k: Number of top results to return
    
    Returns:
        List of ranked records with scores
    """
    searcher = SmartSearch(records)
    return searcher.search(query, top_k=top_k)


def smart_search(query: str, records: Optional[List[Dict[str, Any]]] = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Smart search function (loads records if not provided).
    
    Args:
        query: Search query string
        records: Optional list of cave records (loads from file if None)
        top_k: Number of top results to return
    
    Returns:
        List of ranked records with scores
    """
    if records is None:
        from app.records import load_records
        records = load_records()
    
    return rank_records(records, query, top_k=top_k)


def main():
    """Demonstrate smart search functionality."""
    print("=" * 80)
    print("LENIGUIDE SMART SEARCH - TF-IDF + COSINE SIMILARITY")
    print("Student: Tanmay Subhash Gawali (SJ-52)")
    print("=" * 80)
    
    # Load records
    from app.records import load_records
    records = load_records()
    print(f"\n✓ Loaded {len(records)} cave records")
    
    if SKLEARN_AVAILABLE:
        print("✓ Using scikit-learn TF-IDF vectorization")
    else:
        print("✓ Using pure Python TF-IDF implementation")
    
    # Initialize search
    searcher = SmartSearch(records)
    
    # Test searches
    test_queries = [
        "Kailasa monolithic temple",
        "Buddhist paintings Ajanta",
        "Jain caves Ellora",
        "reclining Buddha",
        "Padmapani mural"
    ]
    
    print("\n" + "=" * 80)
    print("SEARCH TESTS")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 80)
        
        results = searcher.search(query, top_k=3)
        
        for idx, result in enumerate(results, 1):
            site = result['site']
            cave_no = result['cave_no']
            religion = result['religion_period']
            score = result['score']
            
            print(f"  {idx}. [{score:.4f}] {site} Cave {cave_no}")
            print(f"     {religion}")
            print(f"     {result['highlights'][:80]}...")
    
    print("\n" + "=" * 80)
    print("SMART SEARCH TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()

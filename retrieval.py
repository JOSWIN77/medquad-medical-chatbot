"""
retrieval.py
TF-IDF based retrieval engine for MedQuAD Q&A pairs.
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MedRetriever:
    def __init__(self, qa_pairs: list[dict]):
        self.pairs = qa_pairs
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            max_features=50000,
            sublinear_tf=True,
        )
        # Build corpus: combine question + focus for better matching
        corpus = [
            f"{p['question']} {p.get('focus', '')}".lower()
            for p in qa_pairs
        ]
        self.matrix = self.vectorizer.fit_transform(corpus)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Return top_k most relevant Q&A pairs with scores."""
        q_vec = self.vectorizer.transform([query.lower()])
        scores = cosine_similarity(q_vec, self.matrix).flatten()
        top_idx = np.argsort(scores)[::-1][:top_k]
        results = []
        for i in top_idx:
            if scores[i] > 0.05:
                results.append({
                    **self.pairs[i],
                    "score": float(scores[i]),
                    "confidence": _score_to_confidence(float(scores[i])),
                })
        return results


def _score_to_confidence(score: float) -> str:
    if score >= 0.5:
        return "High"
    if score >= 0.25:
        return "Medium"
    return "Low"

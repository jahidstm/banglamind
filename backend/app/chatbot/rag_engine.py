"""
BanglaMind — Lightweight RAG Engine
======================================
ChromaDB-র বদলে TF-IDF + Cosine Similarity ব্যবহার করে।
ফলে:
 - কোনো ভারী dependency নেই (PyTorch, sentence-transformers)
 - Render.com-এ সহজে deploy হয়
 - বাংলা FAQ-এর জন্য যথেষ্ট ভালো কাজ করে

পদ্ধতি:
 1. FAQ data লোড করো
 2. প্রতিটি FAQ question+answer → TF-IDF vector বানাও
 3. User query → TF-IDF vector বানাও
 4. Cosine similarity দিয়ে সবচেয়ে কাছের FAQ খোঁজো
 5. সেই FAQ-এর answer return করো
"""
import os
import json
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(  # banglamind/
    os.path.dirname(           # backend/
        os.path.dirname(       # app/
            os.path.dirname(   # chatbot/
                os.path.abspath(__file__)
            )
        )
    )
)
DEFAULT_FAQ_PATH = os.path.join(BASE_DIR, "data", "sample_faq.json")

# Minimum similarity score — এর নিচে হলে FAQ match ধরা হবে না
SIMILARITY_THRESHOLD = 0.15


class RAGEngine:
    """
    Retrieval-Augmented Generation Engine।
    TF-IDF দিয়ে FAQ থেকে relevant answer খোঁজে।
    """

    def __init__(self, faq_path: str = DEFAULT_FAQ_PATH):
        self.faq_path = faq_path
        self.faqs = []
        self.vectorizer = None
        self.faq_vectors = None
        self.business_name = "আমাদের দোকান"
        self._load_and_index()

    def _load_and_index(self):
        """FAQ লোড করো এবং TF-IDF vector তৈরি করো।"""
        if not os.path.exists(self.faq_path):
            logger.warning(f"FAQ file পাওয়া যায়নি: {self.faq_path}")
            return

        with open(self.faq_path, encoding="utf-8") as f:
            data = json.load(f)

        self.business_name = data.get("business_name", "আমাদের দোকান")
        self.faqs = data.get("faqs", [])

        if not self.faqs:
            logger.warning("FAQ list খালি।")
            return

        # প্রতিটি FAQ-এর জন্য searchable text তৈরি করো
        # question + tags মিলিয়ে index করলে better matching হয়
        corpus = []
        for faq in self.faqs:
            q = faq.get("question", "")
            a = faq.get("answer", "")
            tags = " ".join(faq.get("tags", []))
            # question-কে বেশি weight দেওয়ার জন্য ৩ বার যুক্ত করা হয়েছে
            combined = f"{q} {q} {q} {tags} {a}"
            corpus.append(combined)

        # TF-IDF vectorizer তৈরি করো
        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(2, 4),
            max_features=10000,
            sublinear_tf=True,
        )
        self.faq_vectors = self.vectorizer.fit_transform(corpus)
        logger.info(f"RAG Engine ready: {len(self.faqs)} FAQs indexed for '{self.business_name}'")

    def retrieve(self, query: str, top_k: int = 1) -> list[dict]:
        """
        Query-র সাথে সবচেয়ে মিলসম FAQ খোঁজো।

        Returns:
            list of dicts: [{"faq": {...}, "score": float}]
        """
        if self.vectorizer is None or self.faq_vectors is None:
            return []

        # Query → vector
        query_vector = self.vectorizer.transform([query])

        # Cosine similarity হিসাব করো
        scores = cosine_similarity(query_vector, self.faq_vectors)[0]

        # Top-k সবচেয়ে similar FAQ খোঁজো
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(scores[idx])
            if score >= SIMILARITY_THRESHOLD:
                results.append({
                    "faq":   self.faqs[idx],
                    "score": round(score, 4),
                })

        return results

    def answer(self, query: str) -> dict | None:
        """
        Query-র জন্য সবচেয়ে ভালো FAQ answer return করো।

        Returns:
            {"answer": str, "score": float, "faq_id": str} or None
        """
        results = self.retrieve(query, top_k=1)
        if not results:
            return None

        best = results[0]
        faq  = best["faq"]
        return {
            "answer": faq["answer"],
            "score":  best["score"],
            "faq_id": faq.get("id", "unknown"),
            "question_matched": faq.get("question", ""),
        }

    def reload(self, faq_path: str = None):
        """নতুন FAQ data লোড করো (business owner update করলে)।"""
        if faq_path:
            self.faq_path = faq_path
        self._load_and_index()
        return {"status": "ok", "total_faqs": len(self.faqs)}

    def get_all_faqs(self) -> list:
        """সব FAQ return করো (Dashboard-এ দেখানোর জন্য)।"""
        return self.faqs

    def get_info(self) -> dict:
        """RAG Engine-এর তথ্য return করো।"""
        return {
            "loaded": self.vectorizer is not None,
            "total_faqs": len(self.faqs),
            "business_name": self.business_name,
            "threshold": SIMILARITY_THRESHOLD,
        }


# Global singleton
rag_engine = RAGEngine()

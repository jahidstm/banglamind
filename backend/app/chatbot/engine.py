"""
BanglaMind — Main Chatbot Engine (Full Pipeline)
==================================================
Priority order:
1. RAG (FAQ match) → সবচেয়ে নির্ভুল, ব্যবসার নিজের তথ্য
2. ML Model (high/medium confidence) → trained classifier
3. Rule-based → keyword fallback
4. Default → না বুঝলে সাহায্য চাও
"""
import logging
from backend.app.chatbot.preprocessor import BengaliPreprocessor
from backend.app.chatbot.intent_matcher import IntentMatcher
from backend.app.chatbot.response_templates import ResponseGenerator
from backend.app.chatbot.rag_engine import rag_engine

logger = logging.getLogger(__name__)

# ML Classifier — optional
try:
    from ml.ml_classifier import ml_predict, get_model_info
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML module নেই। Rule-based mode চলছে।")

# RAG minimum confidence
RAG_SCORE_THRESHOLD = 0.20


class ChatbotEngine:
    """
    Full-stack Chatbot Engine:
    RAG (FAQ) → ML → Rule-based → Default
    """
    def __init__(self):
        self.preprocessor      = BengaliPreprocessor()
        self.matcher           = IntentMatcher()
        self.response_generator = ResponseGenerator()

        mode = "RAG + "
        if ML_AVAILABLE and get_model_info().get("loaded"):
            mode += "ML + Rule-based"
        else:
            mode += "Rule-based"
        logger.info(f"ChatbotEngine mode: {mode}")

    def process_message(self, message: str) -> dict:
        """
        Full pipeline:
        1. Preprocess
        2. RAG: FAQ-এ exact/similar answer আছে?
        3. ML: intent classify করো
        4. Rule-based: fallback
        5. Response generate করো
        """
        clean_text = self.preprocessor.process(message)
        lang       = self.preprocessor.detect_language(message)

        # ── Step 1: RAG ───────────────────────────────────────
        rag_result = rag_engine.answer(clean_text)
        if rag_result and rag_result["score"] >= RAG_SCORE_THRESHOLD:
            return {
                "reply": rag_result["answer"],
                "intent": {
                    "tag":        "faq_match",
                    "confidence": "high",
                    "score":      rag_result["score"],
                    "source":     "rag",
                },
                "language": lang,
                "faq_id":   rag_result.get("faq_id"),
            }

        # ── Step 2: ML ────────────────────────────────────────
        ml_result = None
        if ML_AVAILABLE:
            ml_result = ml_predict(clean_text)

        if ml_result and ml_result["confidence"] in ("high", "medium"):
            intent_tag        = str(ml_result["tag"])
            intent_confidence = ml_result["confidence"]
            intent_score      = ml_result["score"]
            source            = "ml"
        else:
            # ── Step 3: Rule-based ────────────────────────────
            rule_result       = self.matcher.match(clean_text)
            intent_tag        = rule_result.tag
            intent_confidence = rule_result.confidence
            intent_score      = rule_result.score
            source            = "rule"

        # ── Step 4: Response ─────────────────────────────────
        reply = self.response_generator.get_reply(intent_tag)

        return {
            "reply": reply,
            "intent": {
                "tag":        intent_tag,
                "confidence": intent_confidence,
                "score":      intent_score,
                "source":     source,
            },
            "language": lang,
        }


# Global singleton
engine = ChatbotEngine()



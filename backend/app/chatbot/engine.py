"""
BanglaMind — Main Chatbot Engine (Hybrid: ML + Rule-based)
============================================================
1. প্রথমে ML model দিয়ে intent detect করার চেষ্টা করে।
2. ML confidence কম হলে Rule-based matcher-এ fallback করে।
3. সবচেয়ে ভালো উত্তর দেয়।
"""
import logging
from backend.app.chatbot.preprocessor import BengaliPreprocessor
from backend.app.chatbot.intent_matcher import IntentMatcher
from backend.app.chatbot.response_templates import ResponseGenerator

logger = logging.getLogger(__name__)

# ML Classifier — lazy import (not required for app startup)
try:
    from ml.ml_classifier import ml_predict, get_model_info
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logger.warning("ML module import করা যায়নি। Rule-based mode চলছে।")


class ChatbotEngine:
    """
    Hybrid Chatbot Engine:
    - ML model (high confidence) → direct answer
    - Rule-based matcher (fallback) → keyword matching
    """
    def __init__(self):
        self.preprocessor = BengaliPreprocessor()
        self.matcher = IntentMatcher()
        self.response_generator = ResponseGenerator()

        if ML_AVAILABLE:
            info = get_model_info()
            if info.get("loaded"):
                logger.info(f"Hybrid mode: ML ({info['accuracy']*100:.1f}% acc) + Rule-based")
            else:
                logger.info("Rule-based mode (ML model পাওয়া যায়নি)")
        else:
            logger.info("Rule-based mode (ML module নেই)")

    def process_message(self, message: str) -> dict:
        """
        মেসেজ প্রসেস করে — Hybrid ML + Rule-based পদ্ধতিতে।
        """
        # Step 1: Preprocess
        clean_text = self.preprocessor.process(message)
        lang = self.preprocessor.detect_language(message)

        # Step 2: ML prediction চেষ্টা করো
        ml_result = None
        if ML_AVAILABLE:
            ml_result = ml_predict(clean_text)

        # Step 3: ML result ভালো হলে ব্যবহার করো, নইলে rule-based
        if ml_result and ml_result["confidence"] in ("high", "medium"):
            intent_tag        = str(ml_result["tag"])   # np.str_ → str
            intent_confidence = ml_result["confidence"]
            intent_score      = ml_result["score"]
            source            = "ml"
        else:
            rule_result       = self.matcher.match(clean_text)
            intent_tag        = rule_result.tag
            intent_confidence = rule_result.confidence
            intent_score      = rule_result.score
            source            = "rule"

        # Step 4: Response generate করো
        reply = self.response_generator.get_reply(intent_tag)

        logger.debug(f"Intent: {intent_tag} | Source: {source} | Confidence: {intent_confidence}")

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


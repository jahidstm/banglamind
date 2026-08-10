"""
BanglaMind — ML Intent Classifier Wrapper
==========================================
Trained scikit-learn model কে load করে intent predict করে।
Rule-based matcher-এর সাথে fallback logic আছে।
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

# Lazy import — শুধুমাত্র যখন ML model ব্যবহার করা হবে
_pipeline = None
_metadata = None

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "ml", "saved_model", "intent_classifier.pkl")
META_PATH  = os.path.join(BASE_DIR, "ml", "saved_model", "model_metadata.json")

# Confidence threshold — এর নিচে হলে rule-based-এ fallback করবে
ML_CONFIDENCE_THRESHOLD = 0.55


def _load_model():
    """Model একবারই load করো (Singleton pattern)।"""
    global _pipeline, _metadata
    if _pipeline is not None:
        return True

    if not os.path.exists(MODEL_PATH):
        logger.warning(f"ML model পাওয়া যায়নি: {MODEL_PATH}. Rule-based mode-এ চলবে।")
        return False

    try:
        import joblib
        _pipeline = joblib.load(MODEL_PATH)
        with open(META_PATH, encoding="utf-8") as f:
            _metadata = json.load(f)
        logger.info(f"ML model লোড হয়েছে। Accuracy: {_metadata.get('accuracy', 'N/A')}")
        return True
    except Exception as e:
        logger.error(f"ML model load করতে সমস্যা: {e}")
        return False


def ml_predict(text: str) -> dict | None:
    """
    ML model দিয়ে intent predict করে।
    Returns: {"tag": str, "confidence": str, "score": float}
    অথবা None যদি model না থাকে বা confidence কম হয়।
    """
    if not _load_model():
        return None

    try:
        proba = _pipeline.predict_proba([text])[0]
        max_proba = float(proba.max())
        predicted_intent = _pipeline.classes_[proba.argmax()]

        if max_proba < ML_CONFIDENCE_THRESHOLD:
            logger.debug(f"ML confidence কম ({max_proba:.2f}), rule-based-এ fallback করছি।")
            return None

        confidence = (
            "high"   if max_proba >= 0.80 else
            "medium" if max_proba >= 0.60 else
            "low"
        )

        return {
            "tag":        predicted_intent,
            "confidence": confidence,
            "score":      round(max_proba, 4),
            "source":     "ml",
        }

    except Exception as e:
        logger.error(f"ML prediction error: {e}")
        return None


def get_model_info() -> dict:
    """Model metadata return করে।"""
    _load_model()
    if _metadata:
        return {
            "loaded": True,
            "accuracy": _metadata.get("accuracy"),
            "cv_accuracy": _metadata.get("cv_accuracy_mean"),
            "model_type": _metadata.get("model_type"),
            "intents": _metadata.get("intents", []),
        }
    return {"loaded": False, "message": "ML model পাওয়া যায়নি। Rule-based mode চলছে।"}

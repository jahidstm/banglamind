"""
BanglaMind -- BanglaBERT Classifier
======================================
Hugging Face Hub থেকে fine-tuned BanglaBERT মডেল লোড করে।
TF-IDF ML মডেলের চেয়ে অনেক বেশি accurate কারণ:
 - এটি প্রতিটি শব্দের context বোঝে
 - বাংলা ভাষার জন্য বিশেষভাবে pre-trained

Priority: BanglaBERT > TF-IDF ML > Rule-based
"""
import os
import json
import logging

logger = logging.getLogger(__name__)

HF_MODEL_REPO = "jahidstm/banglamind-banglabert"
CONFIDENCE_THRESHOLD = 0.60

_model     = None
_tokenizer = None
_id2label  = None
_device    = None


def _load():
    global _model, _tokenizer, _id2label, _device
    if _model is not None:
        return True
    try:
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from huggingface_hub import hf_hub_download

        _device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"BanglaBERT লোড হচ্ছে: {HF_MODEL_REPO} (device={_device})")

        _tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_REPO)
        _model     = AutoModelForSequenceClassification.from_pretrained(
            HF_MODEL_REPO
        ).to(_device)
        _model.eval()

        # label config লোড করো
        cfg_path = hf_hub_download(repo_id=HF_MODEL_REPO, filename="label_config.json")
        with open(cfg_path, encoding="utf-8") as f:
            cfg = json.load(f)
        _id2label = {int(k): v for k, v in cfg["id2label"].items()}

        logger.info(f"BanglaBERT ready! Intents: {list(_id2label.values())}")
        return True

    except Exception as e:
        logger.warning(f"BanglaBERT লোড হয়নি ({e}). ML fallback চলবে।")
        return False


def banglabert_predict(text: str) -> dict | None:
    """
    BanglaBERT দিয়ে intent predict করো।
    Returns: {"tag": str, "confidence": str, "score": float, "source": "banglabert"}
    অথবা None যদি model না থাকে বা confidence কম হয়।
    """
    if not _load():
        return None

    try:
        import torch
        import torch.nn.functional as F

        inputs = _tokenizer(
            text,
            return_tensors  = "pt",
            truncation      = True,
            padding         = True,
            max_length      = 128,
        )
        inputs = {k: v.to(_device) for k, v in inputs.items()}

        with torch.no_grad():
            out   = _model(**inputs)
        probs = F.softmax(out.logits, dim=-1)
        top_prob, top_idx = probs.max(dim=-1)

        score  = float(top_prob.item())
        intent = _id2label[int(top_idx.item())]

        if score < CONFIDENCE_THRESHOLD:
            logger.debug(f"BanglaBERT confidence কম ({score:.2f}), fallback করছি।")
            return None

        confidence = (
            "high"   if score >= 0.85 else
            "medium" if score >= 0.65 else
            "low"
        )
        return {
            "tag":        intent,
            "confidence": confidence,
            "score":      round(score, 4),
            "source":     "banglabert",
        }

    except Exception as e:
        logger.error(f"BanglaBERT prediction error: {e}")
        return None


def is_loaded() -> bool:
    return _model is not None


def get_info() -> dict:
    _load()
    return {
        "loaded":     _model is not None,
        "model_repo": HF_MODEL_REPO,
        "intents":    list(_id2label.values()) if _id2label else [],
        "device":     str(_device) if _device else "not loaded",
    }

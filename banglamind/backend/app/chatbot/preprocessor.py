"""
BanglaMind — Bengali Text Preprocessor
=======================================
Bengali text clean করে chatbot engine-এর জন্য ready করে।
Handles: Unicode normalize, noise removal, Banglish detection
Pure Python implementation — no external NLP dependency.
"""

import re
import unicodedata


# ─── Bengali Unicode Range ────────────────────────────────────────────────────
BENGALI_CHAR_PATTERN = re.compile(r"[\u0980-\u09FF]")

# ─── Common Banglish → Bengali Mapping ───────────────────────────────────────
# দীর্ঘ phrase আগে রাখো (longer match first)
BANGLISH_MAP = {
    # Greetings
    "assalamu alaikum": "আস্সালামু আলাইকুম",
    "assalamualaikum": "আস্সালামু আলাইকুম",
    "salam": "আস্সালামু আলাইকুম",
    "hello": "হ্যালো",
    "hi": "হ্যালো",
    # Thanks
    "thank you": "ধন্যবাদ",
    "thanks": "ধন্যবাদ",
    "dhonnobad": "ধন্যবাদ",
    "dhanyabad": "ধন্যবাদ",
    # Price-related
    "koto taka": "কত টাকা",
    "koto tk": "কত টাকা",
    "price": "দাম",
    "dam": "দাম",
    "cost": "মূল্য",
    "koto": "কত",
    # Location
    "kothay": "কোথায়",
    "kothai": "কোথায়",
    "address": "ঠিকানা",
    "thikana": "ঠিকানা",
    "location": "অবস্থান",
    # Time
    "kokhon": "কখন",
    "khola": "খোলা",
    "bondho": "বন্ধ",
    "open": "খোলা",
    "close": "বন্ধ",
    "time": "সময়",
    "shomoy": "সময়",
    # Common words
    "ami": "আমি",
    "apni": "আপনি",
    "apnar": "আপনার",
    "amar": "আমার",
    "ki": "কি",
    "ache": "আছে",
    "achhe": "আছে",
    "nai": "নাই",
    "nei": "নেই",
    "hobe": "হবে",
    "hoye": "হয়ে",
    "lagbe": "লাগবে",
    "pabo": "পাবো",
    "jabo": "যাবো",
    "dekhte": "দেখতে",
    "janite": "জানতে",
    "jante": "জানতে",
    "bolun": "বলুন",
    "bolen": "বলেন",
    "vai": "ভাই",
    "vaia": "ভাই",
    "bhai": "ভাই",
    "apa": "আপা",
    "order": "অর্ডার",
}

# ─── Emoji Pattern ────────────────────────────────────────────────────────────
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE,
)

# URL pattern
URL_PATTERN = re.compile(r"http[s]?://\S+|www\.\S+")


class BengaliPreprocessor:
    """
    Bengali text preprocessor for BanglaMind chatbot.

    Usage:
        preprocessor = BengaliPreprocessor()
        clean_text = preprocessor.process("আপনাদের   price koto??")
        # Returns: "আপনাদের দাম কত"
    """

    def __init__(self, handle_banglish: bool = True):
        self.handle_banglish = handle_banglish

    def _unicode_normalize(self, text: str) -> str:
        """Unicode NFC normalize করো।"""
        return unicodedata.normalize("NFC", text)

    def _remove_noise(self, text: str) -> str:
        """URL, emoji, extra punctuation remove করো।"""
        text = URL_PATTERN.sub("", text)          # URL remove
        text = EMOJI_PATTERN.sub("", text)        # Emoji remove
        text = re.sub(r"([?!।,।])\1+", r"\1", text)  # ??? → ?
        text = re.sub(r"\s+", " ", text)          # extra spaces
        return text.strip()

    def _convert_banglish(self, text: str) -> str:
        """
        Banglish → Bengali convert করো।
        Example: "price koto?" → "দাম কত?"
        """
        if not self.handle_banglish:
            return text

        result = text.lower()

        # Longer phrases আগে match করো
        for banglish, bengali in sorted(
            BANGLISH_MAP.items(), key=lambda x: len(x[0]), reverse=True
        ):
            result = re.sub(
                r"\b" + re.escape(banglish) + r"\b",
                bengali,
                result,
                flags=re.IGNORECASE,
            )
        return result

    def _normalize_case(self, text: str) -> str:
        """English parts lowercase করো, Bengali unchanged রাখো।"""
        words = text.split()
        normalized = []
        for word in words:
            if BENGALI_CHAR_PATTERN.search(word):
                normalized.append(word)       # Bengali word — unchanged
            else:
                normalized.append(word.lower())  # English word — lowercase
        return " ".join(normalized)

    def process(self, text: str) -> str:
        """
        Main pipeline — সব steps একসাথে।

        Args:
            text: Raw user input (Bengali/Banglish/mixed)

        Returns:
            Clean, normalized text ready for intent matching.
        """
        if not text or not text.strip():
            return ""

        text = self._unicode_normalize(text)   # Step 1
        text = self._remove_noise(text)         # Step 2
        text = self._convert_banglish(text)     # Step 3
        text = self._normalize_case(text)       # Step 4
        return text.strip()

    def is_bengali(self, text: str) -> bool:
        """Text-এ Bengali আছে কিনা check করো।"""
        total = len(text.replace(" ", ""))
        if total == 0:
            return False
        bengali = len(BENGALI_CHAR_PATTERN.findall(text))
        return (bengali / total) > 0.3

    def detect_language(self, text: str) -> str:
        """
        Language detect করো।
        Returns: 'bengali' | 'banglish' | 'english'
        """
        total = len(text.replace(" ", ""))
        if total == 0:
            return "unknown"
        bengali = len(BENGALI_CHAR_PATTERN.findall(text))
        ratio = bengali / total
        if ratio > 0.6:
            return "bengali"
        elif ratio > 0.1:
            return "banglish"
        return "english"

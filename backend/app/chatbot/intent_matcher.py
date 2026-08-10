"""
BanglaMind — Rule-based Intent Matcher
=======================================
Customer-এর message দেখে বুঝবে সে কী জানতে চাইছে।

Logic:
  1. Preprocessed text-এ keyword search করো
  2. সবচেয়ে বেশি keyword match হওয়া intent return করো
  3. কিছু match না হলে 'fallback' return করো
"""

import json
import os
import re
from typing import Optional


# ─── Load Intents ─────────────────────────────────────────────────────────────
_INTENTS_PATH = os.path.join(
    os.path.dirname(__file__),   # chatbot/
    "..", "..", "..",            # app/ → backend/ → project root
    "data", "intents.json"
)


def _load_intents() -> list[dict]:
    """intents.json লোড করো।"""
    path = os.path.abspath(_INTENTS_PATH)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["intents"]


# Module লোড হওয়ার সময় একবারই intents লোড করো (performance)
INTENTS = _load_intents()


# ─── Match Result ─────────────────────────────────────────────────────────────
class MatchResult:
    """Intent matching-এর result।"""

    def __init__(self, tag: str, score: int, matched_keywords: list[str]):
        self.tag = tag
        self.score = score                      # কতটা keyword match হয়েছে
        self.matched_keywords = matched_keywords
        self.confidence = self._calc_confidence()

    def _calc_confidence(self) -> str:
        """Confidence level বের করো।"""
        if self.score >= 3:
            return "high"
        elif self.score >= 1:
            return "medium"
        else:
            return "low"

    def __repr__(self):
        return (
            f"MatchResult(tag='{self.tag}', score={self.score}, "
            f"confidence='{self.confidence}', keywords={self.matched_keywords})"
        )


# ─── Intent Matcher ───────────────────────────────────────────────────────────
class IntentMatcher:
    """
    Rule-based intent matcher for BanglaMind.

    Usage:
        matcher = IntentMatcher()
        result = matcher.match("আপনাদের দাম কত?")
        print(result.tag)        # "price_inquiry"
        print(result.confidence) # "high"
    """

    def __init__(self):
        self.intents = INTENTS

    def _count_keyword_matches(
        self, text: str, keywords: list[str]
    ) -> tuple[int, list[str]]:
        """
        Text-এ কতটা keyword আছে count করো।

        Returns:
            (match_count, matched_keywords_list)
        """
        matched = []
        text_lower = text.lower()

        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Word boundary check — "দাম" যেন "দাম করে" match করে কিন্তু "দামি" না করে
            # Bengali-র জন্য simple substring check বেশি কার্যকর
            if keyword_lower in text_lower:
                matched.append(keyword)

        return len(matched), matched

    def match(self, preprocessed_text: str) -> MatchResult:
        """
        Preprocessed text দেখে সেরা matching intent খোঁজো।

        Args:
            preprocessed_text: BengaliPreprocessor.process() করা text

        Returns:
            MatchResult object
        """
        if not preprocessed_text or not preprocessed_text.strip():
            return MatchResult("fallback", 0, [])

        best_tag = "fallback"
        best_score = 0
        best_keywords = []

        for intent in self.intents:
            # fallback-এর নিজের কোনো keyword নেই, skip করো
            if intent["tag"] == "fallback":
                continue

            score, matched = self._count_keyword_matches(
                preprocessed_text, intent["keywords"]
            )

            # Priority আছে — complaint (priority=3) একটু বেশি ওজন পাবে
            # এতে sensitive message গুলো আগে detect হবে
            adjusted_score = score * (1 / intent.get("priority", 2))

            if adjusted_score > best_score or (
                adjusted_score == best_score and score > best_score
            ):
                best_score = adjusted_score
                best_tag = intent["tag"]
                best_keywords = matched

        return MatchResult(best_tag, best_score, best_keywords)

    def match_all(self, preprocessed_text: str) -> list[MatchResult]:
        """
        সব intents-এর match score return করো (debugging-এর জন্য)।

        Returns:
            List of MatchResult, score-এর নেমে আসা অনুযায়ী sort করা
        """
        results = []
        for intent in self.intents:
            if intent["tag"] == "fallback":
                continue
            score, matched = self._count_keyword_matches(
                preprocessed_text, intent["keywords"]
            )
            if score > 0:
                results.append(MatchResult(intent["tag"], score, matched))

        # Score নেমে আসা অনুযায়ী sort করো
        results.sort(key=lambda r: r.score, reverse=True)

        if not results:
            results.append(MatchResult("fallback", 0, []))

        return results

    def get_intent_tags(self) -> list[str]:
        """সব available intent tag-এর list return করো।"""
        return [i["tag"] for i in self.intents]

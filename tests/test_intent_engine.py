# -*- coding: utf-8 -*-
"""
BanglaMind -- Intent Engine Test
==================================
Run: python tests/test_intent_engine.py
"""
import sys
import io
import os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.chatbot.preprocessor import BengaliPreprocessor
from backend.app.chatbot.intent_matcher import IntentMatcher
from backend.app.chatbot.response_templates import ResponseGenerator

# ─── Setup ────────────────────────────────────────────────────────────────────
preprocessor = BengaliPreprocessor()
matcher = IntentMatcher()
generator = ResponseGenerator(business_config={
    "business_name": "রহিম স্টোর",
    "business_address": "মিরপুর-১০, ঢাকা",
    "business_hours": "সকাল ৯টা - রাত ১০টা (শুক্রবার বন্ধ)",
    "contact_number": "01712-345678",
})

# ─── Colors ───────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def header(title):
    print(f"\n{BOLD}{CYAN}{'='*55}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*55}{RESET}")

def run_chat(user_input: str, expected_intent: str = None):
    """Full pipeline: raw text → preprocessed → intent → reply"""
    clean   = preprocessor.process(user_input)
    result  = matcher.match(clean)
    reply   = generator.get_reply(result.tag)

    # Pass/Fail check
    if expected_intent:
        ok = result.tag == expected_intent
        icon = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
    else:
        icon = f"{CYAN}INFO{RESET}"

    print(f"\n[{icon}] Input    : {YELLOW}{user_input}{RESET}")
    print(f"       Cleaned  : {DIM}{clean}{RESET}")
    print(f"       Intent   : {BOLD}{result.tag}{RESET}  "
          f"(score={result.score:.2f}, conf={result.confidence})")
    if result.matched_keywords:
        print(f"       Keywords : {result.matched_keywords[:5]}")
    print(f"       Reply    : {GREEN}{reply}{RESET}")

# ─── Test Cases ───────────────────────────────────────────────────────────────

header("TEST 1: Greetings")
run_chat("আস্সালামু আলাইকুম",         "greeting")
run_chat("হ্যালো, কেমন আছেন?",         "greeting")
run_chat("Hi, ami jante chaitesi",      "greeting")

header("TEST 2: Price Inquiry")
run_chat("আপনাদের দাম কত?",              "price_inquiry")
run_chat("price koto taka?",             "price_inquiry")
run_chat("এটার মূল্য কত টাকা?",          "price_inquiry")

header("TEST 3: Location")
run_chat("আপনাদের দোকান কোথায়?",         "location")
run_chat("address ta ki?",               "location")
run_chat("কোন এলাকায় আপনারা?",           "location")

header("TEST 4: Business Hours")
run_chat("কখন খোলেন?",                  "hours")
run_chat("আজকে কি খোলা আছে?",            "hours")
run_chat("কয়টায় বন্ধ করেন?",             "hours")

header("TEST 5: Product Info")
run_chat("আপনাদের কাছে কী পাওয়া যায়?",  "product_info")
run_chat("কোন কোন পণ্য আছে?",            "product_info")
run_chat("ki ki ache apnader?",          "product_info")

header("TEST 6: Order")
run_chat("আমি অর্ডার দিতে চাই",           "order")
run_chat("এটা কিনতে চাই",                "order")
run_chat("ami order dite chai",           "order")

header("TEST 7: Delivery")
run_chat("হোম ডেলিভারি আছে?",            "delivery")
run_chat("delivery deben ki?",            "delivery")
run_chat("কতদিনে পৌঁছাবে?",              "delivery")

header("TEST 8: Contact")
run_chat("আপনাদের ফোন নম্বর কত?",         "contact")
run_chat("contact number ta din",         "contact")
run_chat("কীভাবে যোগাযোগ করবো?",          "contact")

header("TEST 9: Complaint")
run_chat("পণ্যটা নষ্ট এসেছে",             "complaint")
run_chat("আমার refund chai",              "complaint")
run_chat("সমস্যা হচ্ছে পণ্যে",            "complaint")

header("TEST 10: Thanks")
run_chat("ধন্যবাদ আপনাকে",               "thanks")
run_chat("thanks bhai",                   "thanks")
run_chat("আল্লাহ হাফেজ",                  "thanks")

header("TEST 11: Fallback (Unknown)")
run_chat("ektu bolben please?",           "fallback")
run_chat("আমি বুঝতে পারছি না",            "fallback")

header("TEST 12: Multi-keyword Match Debug")
# দেখি multiple keywords থাকলে কী হয়
test_msg = "ভাই দাম কত আর কোথায় দোকান?"
clean = preprocessor.process(test_msg)
all_results = matcher.match_all(clean)
print(f"\n  Input: '{test_msg}'")
print(f"  Cleaned: '{clean}'")
print(f"  All matches (sorted by score):")
for r in all_results:
    print(f"    → {r.tag:15s} score={r.score:.2f}  keywords={r.matched_keywords}")

print(f"\n{BOLD}{GREEN}{'='*55}{RESET}")
print(f"{BOLD}{GREEN}  Intent Engine Tests Complete!{RESET}")
print(f"{BOLD}{GREEN}{'='*55}{RESET}\n")

# -*- coding: utf-8 -*-
"""
BanglaMind -- Preprocessor Test
Run: python tests/test_preprocessor.py
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sys
import os

# Path setup — project root থেকে run করার জন্য
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.chatbot.preprocessor import BengaliPreprocessor

# ─── Test Setup ───────────────────────────────────────────────────────────────
preprocessor = BengaliPreprocessor()

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'─'*50}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'─'*50}{RESET}")


def run_test(description: str, input_text: str, expected_contains: str = None):
    """একটা test run করো এবং result দেখাও।"""
    result = preprocessor.process(input_text)
    lang = preprocessor.detect_language(input_text)

    status = f"{GREEN}✅{RESET}"

    # Expected text check (optional)
    if expected_contains and expected_contains not in result:
        status = f"{YELLOW}⚠️ {RESET}"

    print(f"\n{status} {BOLD}{description}{RESET}")
    print(f"   Input  : {YELLOW}{repr(input_text)}{RESET}")
    print(f"   Output : {GREEN}{repr(result)}{RESET}")
    print(f"   Lang   : [{lang}]")


# ─── Test Cases ───────────────────────────────────────────────────────────────

print_header("TEST 1: Basic Bengali Cleaning")
run_test(
    "Normal Bengali text",
    "আপনাদের দোকান কোথায়?",
)
run_test(
    "Extra spaces remove",
    "আমাদের   দাম   কত   টাকা?",
)
run_test(
    "Multiple question marks",
    "দাম কত???",
    "দাম কত",
)

print_header("TEST 2: Banglish Conversion")
run_test(
    "Pure Banglish",
    "price koto?",
    "দাম",
)
run_test(
    "Mixed Banglish-Bengali",
    "apnar দোকান কোথায়?",
    "আপনার",
)
run_test(
    "English greetings",
    "hello, ami jante chai",
    "হ্যালো",
)
run_test(
    "Thanks in English",
    "thanks apnake",
    "ধন্যবাদ",
)

print_header("TEST 3: Noise Removal")
run_test(
    "Emoji with Bengali",
    "আপনাদের দাম কত? 😊🙏",
)
run_test(
    "Mixed noise",
    "  আপনাদের  ঠিকানা  কি???  ",
)

print_header("TEST 4: Language Detection")
tests = [
    ("আপনাদের দোকান কোথায়?", "bengali"),
    ("price koto taka?", "banglish"),
    ("what is your address?", "english"),
    ("ami jante chai আপনার price", "banglish"),
]
for text, expected in tests:
    detected = preprocessor.detect_language(text)
    icon = f"{GREEN}✅{RESET}" if detected == expected else f"{RED}❌{RESET}"
    print(f"\n  {icon} '{text[:35]}...' " if len(text) > 35 else f"\n  {icon} '{text}'")
    print(f"     Expected: {expected} | Got: {detected}")

print_header("TEST 5: Real Customer Messages")
real_messages = [
    "vai apnader price ta koto?",
    "আপনাদের দোকান কি এখন খোলা আছে?",
    "hello! ami order dite chai",
    "কোথায় আছেন আপনারা? address দেন",
    "thanks vaia, dhonnobad",
    "আপনাদের কাছে কি পণ্য আছে?",
]
for msg in real_messages:
    result = preprocessor.process(msg)
    print(f"\n  📨 Input : {YELLOW}{msg}{RESET}")
    print(f"  ✨ Output: {GREEN}{result}{RESET}")

print(f"\n{BOLD}{GREEN}{'='*50}{RESET}")
print(f"{BOLD}{GREEN}  ✅ Preprocessor tests completed!{RESET}")
print(f"{BOLD}{GREEN}{'='*50}{RESET}\n")

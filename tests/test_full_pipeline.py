import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.chatbot.engine import engine

TESTS = [
    # RAG থেকে আসা উচিত
    ("আপনাদের দোকান কোথায়?",       "rag"),
    ("bkash দিয়ে কি পেমেন্ট হয়?",   "rag"),
    ("রিফান্ড পলিসি কী?",            "rag"),
    ("ডেলিভারি কতদিনে আসবে?",        "rag"),
    ("ওয়ারেন্টি কত দিনের?",         "rag"),
    # ML/Rule থেকে আসা উচিত
    ("আস্সালামু আলাইকুম",            "ml"),
    ("ধন্যবাদ অনেক",                 "ml"),
]

print("\n" + "=" * 65)
print("  BanglaMind — Full Pipeline Test (RAG + ML + Rule-based)")
print("=" * 65)

passed = 0
for text, expected_source in TESTS:
    r = engine.process_message(text)
    i = r["intent"]
    actual = i["source"]
    ok = "✅" if actual == expected_source else "⚠️"
    if actual == expected_source:
        passed += 1
    print(f"\n{ok} [{actual.upper():4}] \"{text}\"")
    print(f"   Intent : {i['tag']} ({i['confidence']}, {i['score']:.0%})")
    print(f"   Reply  : {r['reply'][:70]}...")

print(f"\n{'='*65}")
print(f"  ফলাফল: {passed}/{len(TESTS)} test সঠিক উৎস থেকে এসেছে")
print(f"{'='*65}\n")

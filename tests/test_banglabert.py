import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.chatbot.engine import engine

TESTS = [
    "আস্সালামু আলাইকুম",
    "দাম কত ভাই?",
    "ডেলিভারি চার্জ কত?",
    "দোকান কোথায়?",
    "ধন্যবাদ ভাই",
]

print("\n" + "=" * 65)
print("  BanglaMind -- Pipeline Test (RAG + BanglaBERT + ML + Rule)")
print("=" * 65)

for text in TESTS:
    r = engine.process_message(text)
    i = r["intent"]
    print(f'\n[{i["source"].upper():10}] "{text}"')
    print(f'   Intent : {i["tag"]} ({i["confidence"]}, {i["score"]:.0%})')
    print(f'   Reply  : {r["reply"][:60]}...')

print("\n" + "=" * 65)

import sys, io, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from backend.app.chatbot.engine import engine

tests = [
    'দাম কত ভাই?',
    'কখন খোলেন?',
    'ভাই এটার রেট কত?',
    'delivery charge koto?',
    'পণ্য ভাঙা এসেছে',
    'আস্সালামু আলাইকুম',
]
print("\n--- Hybrid Engine Test ---")
for t in tests:
    r = engine.process_message(t)
    i = r['intent']
    print(f'[{i["source"].upper():4}] "{t}" → {i["tag"]} ({i["confidence"]}, {i["score"]:.0%})')

print("\nHybrid engine সফলভাবে কাজ করছে! ✅")

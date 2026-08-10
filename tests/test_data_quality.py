"""
BanglaMind — Data Quality Check
==================================
Training dataset-এর মান যাচাই করে।
"""
import csv
import os
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def check_dataset(csv_path: str):
    """CSV ডাটাসেটের মান যাচাই করে।"""

    if not os.path.exists(csv_path):
        print(f"❌ ফাইল পাওয়া যায়নি: {csv_path}")
        return

    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    print("=" * 55)
    print("  BanglaMind — Data Quality Report")
    print("=" * 55)

    # 1. মোট ডাটা
    total = len(rows)
    print(f"\n📦 মোট Training উদাহরণ: {total}")

    # 2. প্রতিটি ইনটেন্টে কতটি
    intent_counts = {}
    for row in rows:
        intent = row.get("intent", "unknown")
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

    print(f"\n📊 Intent Distribution:")
    print(f"  {'Intent':<22} {'Count':>6}  {'Bar'}")
    print(f"  {'-'*50}")
    for intent, count in sorted(intent_counts.items()):
        bar = "█" * (count // 5)
        print(f"  {intent:<22} {count:>6}  {bar}")

    # 3. ডুপ্লিকেট চেক
    texts = [row.get("text", "").strip().lower() for row in rows]
    duplicates = len(texts) - len(set(texts))
    print(f"\n🔍 Duplicate চেক: ", end="")
    if duplicates == 0:
        print(f"✅ কোনো Duplicate নেই")
    else:
        print(f"⚠️  {duplicates} টি Duplicate পাওয়া গেছে")

    # 4. খালি টেক্সট চেক
    empty = sum(1 for t in texts if not t)
    print(f"🔍 খালি Text চেক: ", end="")
    if empty == 0:
        print(f"✅ কোনো খালি Text নেই")
    else:
        print(f"⚠️  {empty} টি খালি Text পাওয়া গেছে")

    # 5. সবচেয়ে ছোট ও বড় বাক্য
    sorted_by_len = sorted(rows, key=lambda r: len(r.get("text", "")))
    print(f"\n📏 সবচেয়ে ছোট বাক্য: \"{sorted_by_len[0]['text']}\" ({sorted_by_len[0]['intent']})")
    print(f"📏 সবচেয়ে বড় বাক্য : \"{sorted_by_len[-1]['text']}\" ({sorted_by_len[-1]['intent']})")

    # 6. গড় বাক্য দৈর্ঘ্য
    avg_len = sum(len(r.get("text","")) for r in rows) / total
    print(f"📏 গড় বাক্যের দৈর্ঘ্য: {avg_len:.1f} অক্ষর")

    # 7. ক্লাস ব্যালেন্স চেক
    max_count = max(intent_counts.values())
    min_count = min(intent_counts.values())
    ratio = max_count / min_count
    print(f"\n⚖️  Class Balance:")
    print(f"   সর্বোচ্চ: {max_count}, সর্বনিম্ন: {min_count}, অনুপাত: {ratio:.2f}x")
    if ratio <= 1.5:
        print("   ✅ ডাটা ভালোভাবে ব্যালেন্সড")
    elif ratio <= 2.0:
        print("   ⚠️  কিছুটা imbalanced, ML-এ সমস্যা নাও হতে পারে")
    else:
        print("   ❌ Imbalanced! বেশি কম থাকা ক্লাসে আরও ডাটা যুক্ত করুন")

    print("\n" + "=" * 55)
    print("  ✅ Quality Check সম্পন্ন!")
    print("=" * 55)


if __name__ == "__main__":
    check_dataset(os.path.join("data", "intents_dataset.csv"))

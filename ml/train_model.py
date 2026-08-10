"""
BanglaMind — ML Intent Classifier Training
============================================
TF-IDF + Logistic Regression দিয়ে বাংলা/বাংলিশ
intent classification মডেল train করে।

Run করার কমান্ড:
    python ml/train_model.py
"""
import os
import csv
import json
import joblib
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

# ─── Paths ───────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH  = os.path.join(BASE_DIR, "data", "intents_dataset.csv")
MODEL_DIR  = os.path.join(BASE_DIR, "ml", "saved_model")
MODEL_PATH = os.path.join(MODEL_DIR, "intent_classifier.pkl")
META_PATH  = os.path.join(MODEL_DIR, "model_metadata.json")


def load_data(csv_path: str):
    """CSV থেকে training data load করে।"""
    texts, labels = [], []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            texts.append(row["text"])
            labels.append(row["intent"])
    return texts, labels


def build_pipeline() -> Pipeline:
    """
    TF-IDF + Logistic Regression Pipeline তৈরি করে।

    TF-IDF: প্রতিটি শব্দকে সংখ্যায় রূপান্তর করে।
    Logistic Regression: সেই সংখ্যা দেখে সিদ্ধান্ত নেয়।
    """
    from sklearn.pipeline import FeatureUnion
    from sklearn.feature_extraction.text import TfidfVectorizer as TV

    # Word-level + Character-level features একসাথে
    features = FeatureUnion([
        ("word", TV(
            analyzer="word",
            ngram_range=(1, 2),
            max_features=8000,
            sublinear_tf=True,
        )),
        ("char", TV(
            analyzer="char_wb",
            ngram_range=(2, 5),
            max_features=12000,
            sublinear_tf=True,
        )),
    ])

    pipeline = Pipeline([
        ("features", features),
        (
            "clf",
            LogisticRegression(
                max_iter=2000,
                C=10.0,
                solver="lbfgs",
            ),
        ),
    ])
    return pipeline


def evaluate_model(pipeline, X_test, y_test):
    """Model-এর performance মূল্যায়ন করে।"""
    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    cm = confusion_matrix(y_test, y_pred)
    return accuracy, report, y_pred, cm


def train_and_save():
    print("\n" + "=" * 55)
    print("  BanglaMind — ML Training শুরু হচ্ছে...")
    print("=" * 55)

    # 1. Data Load
    print("\n📂 Training data load করছি...")
    texts, labels = load_data(DATA_PATH)
    unique_intents = sorted(set(labels))
    print(f"   মোট উদাহরণ : {len(texts)}")
    print(f"   মোট Intent  : {len(unique_intents)}")

    # 2. Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        texts, labels, test_size=0.2, random_state=42, stratify=labels
    )
    print(f"   Train set   : {len(X_train)} টি")
    print(f"   Test set    : {len(X_test)} টি")

    # 3. Pipeline Build & Train
    print("\n🤖 Model Train করছি (TF-IDF + Logistic Regression)...")
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    print("   ✅ Training সম্পন্ন!")

    # 4. Cross-Validation
    print("\n🔀 Cross-Validation চলছে (5-fold)...")
    cv_scores = cross_val_score(pipeline, texts, labels, cv=5, scoring="accuracy")
    print(f"   CV Accuracy: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    print(f"   প্রতিটি Fold: {[f'{s:.3f}' for s in cv_scores]}")

    # 5. Test Set Evaluation
    print("\n📊 Test Set Evaluation...")
    accuracy, report, y_pred, cm = evaluate_model(pipeline, X_test, y_test)
    print(f"   Test Accuracy: {accuracy * 100:.2f}%")

    # 6. Per-Intent Performance
    print(f"\n📋 প্রতিটি Intent-এর Performance:")
    print(f"   {'Intent':<22} {'Precision':>9} {'Recall':>8} {'F1':>8}")
    print(f"   {'-'*52}")
    for intent in unique_intents:
        if intent in report:
            p = report[intent]["precision"]
            r = report[intent]["recall"]
            f = report[intent]["f1-score"]
            emoji = "✅" if f >= 0.85 else "⚠️"
            print(f"   {intent:<22} {p:>9.3f} {r:>8.3f} {f:>8.3f} {emoji}")

    # 7. Save Model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    # Metadata save করো
    metadata = {
        "accuracy": round(accuracy, 4),
        "cv_accuracy_mean": round(float(cv_scores.mean()), 4),
        "cv_accuracy_std": round(float(cv_scores.std()), 4),
        "intents": unique_intents,
        "train_size": len(X_train),
        "test_size": len(X_test),
        "model_type": "TF-IDF + LogisticRegression",
        "vectorizer_params": {
            "analyzer": "char_wb",
            "ngram_range": [2, 4],
            "max_features": 15000,
        },
    }
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Model সেভ হয়েছে: {MODEL_PATH}")
    print(f"💾 Metadata সেভ হয়েছে: {META_PATH}")

    # 8. Quick Manual Test
    print("\n🧪 Quick Test (৫টি নমুনা প্রশ্ন):")
    test_cases = [
        ("দাম কত ভাই?",           "price_inquiry"),
        ("কখন খোলেন?",            "hours"),
        ("আস্সালামু আলাইকুম",    "greeting"),
        ("ডেলিভারি আছে?",         "delivery"),
        ("পণ্য নষ্ট এসেছে refund chai", "complaint"),
    ]
    for text, expected in test_cases:
        predicted = pipeline.predict([text])[0]
        proba = pipeline.predict_proba([text]).max()
        status = "✅" if predicted == expected else "❌"
        print(f"   {status} \"{text[:30]}\"")
        print(f"      Expected: {expected} | Got: {predicted} ({proba:.0%})")

    print("\n" + "=" * 55)
    print(f"  ✅ সব শেষ! Accuracy: {accuracy * 100:.2f}%")
    print("=" * 55 + "\n")

    return pipeline, accuracy


if __name__ == "__main__":
    train_and_save()

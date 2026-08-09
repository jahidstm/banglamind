# 🤖 BanglaMind — Bengali AI Chatbot SaaS

BanglaMind is an intelligent conversational AI system designed for Bangladeshi small and medium-sized enterprises (SMEs). It automatically handles customer inquiries in Bengali and Banglish across platforms like Facebook Messenger and WhatsApp.

---

## 📌 Features & Development Progress

### Phase 1: Foundation (In Progress)
- [x] Project Structure & Environment Setup
- [x] Bengali Text Preprocessor (`preprocessor.py`)
  - Unicode NFC Normalization
  - Noise & Emoji Removal
  - Banglish-to-Bengali Token Mapping (`price` → `দাম`, `address` → `ঠিকানা`, etc.)
  - Language Detection (Bengali / Banglish / English)
- [ ] Rule-based Intent Engine
- [ ] FastAPI Backend Endpoint
- [ ] Interactive Demo Web UI

---

## 🛠️ Project Structure

```
banglamind/
├── backend/
│   └── app/
│       └── chatbot/
│           ├── __init__.py
│           └── preprocessor.py   # Bengali NLP text cleaning engine
├── tests/
│   └── test_preprocessor.py      # Preprocessor test suite
├── data/                         # Datasets & FAQs
├── requirements.txt              # Project dependencies
└── README.md
```

---

## 🧪 Testing the Preprocessor

To run the preprocessor test suite:

```bash
python tests/test_preprocessor.py
```

---

## 🚀 Tech Stack

- **Backend:** FastAPI, Python 3.13
- **NLP:** Custom Bengali Preprocessor (NFC Normalization, Banglish Mapping)
- **Database (Upcoming):** ChromaDB (RAG), PostgreSQL / Supabase
- **Models (Upcoming):** Scikit-learn, PyTorch, Fine-tuned BanglaBERT

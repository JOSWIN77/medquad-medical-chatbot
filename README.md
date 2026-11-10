# 🏥 MedQuAD Medical Q&A Chatbot

A specialized medical question-answering chatbot built using the [MedQuAD Dataset](https://github.com/abachaa/MedQuAD) from NIH.

## ✨ Features
- 🔍 **TF-IDF Retrieval** — Finds best-matching answers from 1,000+ Q&A pairs
- 🏷️ **Medical NER** — Detects Symptoms, Diseases, Treatments, Body Parts, Drugs
- 📊 **Confidence Scoring** — High / Medium / Low per result
- 💬 **Interactive Streamlit UI** — Chat bubbles, expandable result cards, sidebar stats
- 🗃️ **Local Caching** — Downloads once, loads instantly after

## 📁 Project Structure
```
├── app.py           # Streamlit UI
├── data_loader.py   # Downloads & parses MedQuAD XML from GitHub
├── retrieval.py     # TF-IDF search engine with cosine similarity
├── ner.py           # Medical entity recognition (5 entity types)
├── requirements.txt # Dependencies
└── run.bat          # One-click launcher (Windows)
```

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python -m streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

> ⚠️ First run downloads MedQuAD data from GitHub (~1–2 min). Subsequent runs load from local cache instantly.

## 💡 Sample Questions
- What are the symptoms of diabetes?
- How is cancer treated?
- What causes hypertension?
- What is Alzheimer's disease?
- What are treatments for asthma?

## 🧠 Tech Stack
- **Streamlit** — UI framework
- **scikit-learn** — TF-IDF vectorizer + cosine similarity
- **lxml / xml.etree** — MedQuAD XML parsing
- **MedQuAD Dataset** — NIH medical Q&A pairs

## ⚠️ Disclaimer
This chatbot is for **informational purposes only** and is **not a substitute for professional medical advice**.

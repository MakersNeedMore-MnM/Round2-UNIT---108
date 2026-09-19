
# ⚖️ LexaGuard AI

### Autonomous Legal Contract Intelligence System

**Translate complex contracts into clear, actionable insights — in minutes.**

---

## 📌 What Is LexaGuard AI?

LexaGuard AI is a **multi-agent legal contract intelligence platform** that automatically:

- Ingests contracts in **PDF, DOCX, or plain text** format
- Segments and classifies every clause into **10 legal categories**
- Compares clauses against **50+ industry-standard templates** using Advanced RAG
- Assigns **HIGH / MEDIUM / LOW risk scores** per clause with legal reasoning
- Generates **plain-English summaries**, **redline suggestions**, and **negotiation tips**
- Exports full **PDF, DOCX, and JSON reports** in one click

> LexaGuard AI acts as a **legal assistant**.
> It surfaces risks and suggests improvements — the final decision always rests with you.

---


## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 📄 **Multi-format Ingestion** | PDF, DOCX, TXT — drag and drop |
| ✂️ **Smart Clause Segmentation** | Regex + LLM boundary detection |
| 🏷️ **Multi-Category Classification** | Liability, IP, Termination, Payment, Confidentiality, Indemnity, Dispute Resolution, Force Majeure, Warranties, General |
| 📊 **Advanced RAG Comparison** | Hybrid BM25 + semantic search over 50+ standard templates |
| ⚠️ **Risk Scoring** | HIGH / MEDIUM / LOW per clause + overall 0–100 score |
| ⚖️ **Legal Reasoning** | Chain-of-thought impact analysis per risky clause |
| 💬 **Plain English Translation** | Grade-8 reading level summaries for non-lawyers |
| ✏️ **Auto Redlining** | Safer clause rewrites + negotiation strategy per issue |
| 📄 **Report Export** | One-click PDF, DOCX, and JSON download |
| 🤖 **Chat Assistant** | Contract-aware Q&A — ask anything about your contract |

---

### Agent Responsibilities

| Agent | Name | Responsibility |
|-------|------|----------------|
| A-01 | Document Parser | Extracts text & metadata from PDF / DOCX / TXT |
| A-02 | Clause Segmenter | Splits contract into atomic clauses using regex + LLM |
| A-03 | Clause Classifier | Tags each clause into multi legal categories with confidence score |
| A-04 | Key Info Extractor | Pulls parties, dates, amounts, penalties, obligations |
| A-05 | Template Comparator | RAG retrieval — hybrid BM25 + semantic deviation scoring |
| A-06 | Risk Detector | HIGH / MEDIUM / LOW per clause — hybrid rule engine + LLM |
| A-07 | Legal Reasoner | Chain-of-thought legal impact analysis + precedent lookup |
| A-08 | Plain Language | Converts legal jargon to Grade-8 English |
| A-09 | Redlining Agent | Auto-suggests safer rewrites + negotiation strategy |
| A-10 | Report Generator | Assembles full report → PDF / DOCX / JSON |

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10 |
| **LLM** | Gemini |
| **Agent Framework** | LangChain + LangGraph |
| **Vector Database** | ChromaDB |
| **Embeddings** | text-embedding-3-small (hybrid BM25 + dense) |
| **Document Parsing** | PyMuPDF · pdfplumber · python-docx |
| **UI Framework** | Streamlit |
| **Report Generation** | ReportLab (PDF) · python-docx (DOCX) |
| **Storage** | SQLite + ChromaDB |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A Gemini API key

### Local Setup

**1. Clone the repository**
```bash
git clone repository URL
cd project name 
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**

Create the file `.streamlit/secrets.toml` and paste:
```toml
API_KEY = "YOUR_KEY_HERE"
```

**4. Run the app**
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---


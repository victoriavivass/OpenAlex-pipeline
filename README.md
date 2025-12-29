# OpenAlex Journal Pipeline

A reproducible Python pipeline to extract, clean, analyse, and visualise the prevalence of AI- and NLP-related concepts in academic journal articles using the **OpenAlex API**.

The pipeline is designed for comparative analyses across disciplines and is currently applied to **Sociology** and **Political Science** journals, as part of my work as a research assistant at IPP Computational Social Sciences.

---

## Inspiration

This project is built on top of the **pyalex** library:

<p align="center">
  <a href="https://github.com/J535D165/pyalex">
    <img src= "https://raw.githubusercontent.com/J535D165/pyalex/main/pyalex_repocard.svg" alt="pyalex logo" width="300"/>
  </a>
</p>

> **pyalex** — A Python interface to the OpenAlex API  
> https://github.com/J535D165/pyalex

Please cite or acknowledge **pyalex** if using or extending this pipeline.

---

## 📂 Project Structure

```text
OpenAlex-pipeline/
│
├── data/
│   └── top50_Soc_Pol.xlsx
│
├── scripts/
│   ├── 00_smoke_test.py
│   ├── 01_extract.py
│   ├── 02_clean.py
│   ├── 03_analyse.py
│   └── 04_visualise.py
│
├── outputs/
│   └── figures/
│       ├── keywords_trends_color_combined.png
│       └── keywords_trends_interactive_combined.html
│
├── src/
│   └── openalex_pipeline/
│       ├── __init__.py
│       └── utils.py
│
├── notebook/
│   └── openalex_pipeline.ipynb
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🔁 Pipeline Overview

### 01 — Extract
- Reads journal lists from Excel
- Queries the OpenAlex API for all works since 2010
- Stores raw OpenAlex responses

### 02 — Clean
- Reconstructs abstracts from inverted indexes
- Applies strict regex-based keyword matching

### 03 — Analyse
- Ensures unique article counting
- Computes yearly totals and keyword shares

### 04 — Visualise
- Static PNG and interactive HTML figures
- Supports single and combined discipline modes

---

## ▶️ Running the Pipeline

```bash
python scripts/01_extract.py --sheet Sociology
python scripts/02_clean.py -- sheet Sociology 
python scripts/03_analyse.py -- sheet Sociology 
python scripts/04_visualise.py
```

---

## 📦 Dependencies

```bash
pip install -r requirements.txt
```

---

## ✨ Author

Victoria Vivas  
IPP Computational Social Sciences

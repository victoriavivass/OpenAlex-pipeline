# OpenAlex Journal Pipeline

A reproducible Python pipeline designed to support large-scale bibliographic reviews in the social sciences, with a focus on the diffusion and use of **AI and NLP methods**, particularly **Large Language Models (LLMs)** and **BERT-based architectures**, in academic research.

This project was developed as part of my work as a research assistant at **IPP Computational Social Sciences**, within a broader literature review on the applications of LLMs in **Sociology** and **Political Science**, especially for **text classification and automated text analysis tasks**.

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

## Motivation and Research Context

In the context of the IPP project, we aimed to identify and analyse academic articles published since 2010 that apply or discuss modern NLP and AI techniques, within leading journals in Sociology and Political Science.

However, manually identifying relevant publications across the top 25–50 journals per discipline proved to be infeasible due to:
- the large volume of publications,
- heterogeneous terminology across journals and years,
- and the rapid evolution of AI-related concepts.

To address this challenge, this pipeline automates:
1. the retrieval of journal articles and abstracts from **OpenAlex**,
2. the detection of relevant AI/NLP concepts using **regex-based keyword matching**, and
3. the computation of how the **prevalence of these concepts has evolved over time** within and across disciplines.

The goal is not only to identify relevant articles, but also to quantify how the presence of these methods has evolved over time within top-tier journals in both disciplines.

---

## What the Pipeline Does

The pipeline:
- Automatically retrieves all journal articles published since 2010 from a predefined list of top journals.
- Reconstructs abstracts from OpenAlex inverted indexes.
- Identifies AI- and NLP-related concepts using regular expressions.
- Computes yearly counts and proportions of articles mentioning these concepts.
- Produces both static and interactive visualisations to explore trends over time.

The final outputs allow us to assess whether—and how—the presence of AI- and LLM-related methods in top social science journals has increased over the past decade.

---

## Methodological Note

Keyword detection relies on **regular expression matching**, which enables transparent and reproducible filtering but may also:
- miss relevant articles that use unconventional terminology,
- or include false positives in ambiguous cases.

To mitigate this, potentially ambiguous terms (e.g. *AI*) are matched using **context-aware regex patterns** (e.g. requiring co-occurrence with words such as *model*).  
This trade-off between precision and recall is a methodological limitation of this approach.

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
- Queries the OpenAlex API for all works published since 2010
- Stores raw OpenAlex responses for reproducibility

### 02 — Clean
- Reconstructs abstracts from inverted indexes
- Applies strict regex-based keyword matching

### 03 — Analyse
- Ensures unique article counting
- Computes yearly totals and keyword prevalence metrics

### 04 — Visualise
- Produces static (PNG) and interactive (HTML) figures
- Supports single-discipline and combined-discipline analyses
  
---

## ▶️ Running the Pipeline

```bash
python scripts/01_extract.py --sheet Sociology
python scripts/02_clean.py -- sheet Sociology 
python scripts/03_analyse.py -- sheet Sociology 
```

```bash
python scripts/01_extract.py --sheet Political_Science
python scripts/02_clean.py -- sheet Political_Science
python scripts/03_analyse.py -- sheet Political_Science
```

By default, the visualisation step can operate in combined mode, aggregating results from Sociology and Political Science to compute overall yearly proportions.

```bash
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



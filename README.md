# OpenAlex Journal Pipeline

<p align="center">
  <img src="https://raw.githubusercontent.com/victoriavivass/OpenAlex-pipeline/main/pyalex_logo.png" width="330">
</p>

This repository contains a Python pipeline developed as part of my work as Research Assistant in the **IPP Computational Social Sciences**.   
Its purpose is to **accelerate literature review workflows** by automatically retrieving journal information, article metadata, abstracts, and keyword-based matches from the repository **OpenAlex**.

The pipeline relies on the existing Python module **pyalex**, created and maintained by:  
 https://github.com/J535D165/pyalex  
All user-designed functions in this project build on top of pyalex’s API structure and rely on it for all OpenAlex interactions.

---

## Features

- Match journals to OpenAlex using **ISSN** or **journal name**
- Retrieve:
  - article titles  
  - DOIs  
  - authors  
  - publication years  
  - abstracts (fully reconstructed from OpenAlex's inverted index)  
- Perform **keyword searches** across articles from selected journals
- Detect appearance of keywords inside abstracts
- Export results to a clean **Excel file**
- Provide a command-line tool (`openalex-journal-pipeline`) for reproducible execution

---

## Project Structure


---

## Installation

Clone the repository:

```bash
git clone https://github.com/victoriavivass/OpenAlex-pipeline.git
cd OpenAlex-pipeline
```

Install dependencies

```bash
pip install -r requirements.txt
```

Install the package locally:

```bash
pip install -e .
```

# ICP Signal Scraper

## Overview

This project identifies potential ICP (Ideal Customer Profile) companies by scraping company websites and searching for predefined AI/ML infrastructure signals.

The scraper analyzes company websites, career pages, engineering blogs, technology pages, product pages, and solution pages to detect signals related to AI, LLMs, MLOps, inference infrastructure, and model deployment.

Companies are scored based on signal strength and ranked accordingly.

The final output is generated as an Excel spreadsheet containing the top-ranked companies.

---

## Features

- Multi-page website discovery
- Career page scraping
- Engineering and technology page scraping
- AI/ML signal detection
- Weighted scoring system
- Parallel processing for faster execution
- Automatic ranking of companies
- Top 15 company selection
- Excel output generation

---

## Signals Used

### Weak Signals (1 Point)

- AI
- Artificial Intelligence
- Machine Learning

### Medium Signals (3 Points)

- MLOps
- GenAI
- TensorFlow
- PyTorch
- Llama
- DeepSeek
- Whisper
- Flux

### Strong Signals (10 Points)

- LLM
- vLLM
- TensorRT
- RAG
- Fine Tuning
- Inference
- Model Serving

---

## Scoring Logic

Each detected signal contributes a predefined weight to the company score.

Example:

LLM + vLLM + TensorRT

Score:

10 + 10 + 10 = 30

Companies are ranked by score in descending order.

If two companies have the same score, the company with more strong signals is ranked higher.

---

## Discovery Pages

The scraper checks:

- Homepage
- Careers
- Career
- Jobs
- Join Us
- Work With Us
- Openings
- Vacancies
- Opportunities
- Hiring
- Blog
- Engineering
- Technology
- Platform
- AI
- ML
- Products
- Solutions

---

## Output

The final spreadsheet contains:

| Column |
|----------|
| Company Name |
| Signal Found |
| Why It Suggests Buying Intent |
| Score |
| Source URL |

Example:

| Company Name | Signal Found | Why It Suggests Buying Intent | Score |
|-------------|-------------|--------|
| Example AI | llm, rag, vllm | Company appears to be building production-grade LLM.. | 30 |

---

## Installation

Install dependencies:
pip install -r requirements.txt

## NOTE

Running the Project:
python SignalScraper.py

Input file:
output/companies.csv

Output file:
output/icp_signals_output.xlsx


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
- Client signal extraction
- Existing client website analysis
- Medium and strong signal matching
- Matched client identification
- Similar-customer discovery

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

## Client Matching Logic

The project also analyzes existing client websites and extracts AI-related signals.

Client matching is performed using:

- Medium Signals
- Strong Signals

Weak signals are intentionally ignored during matching to reduce noise.

If a prospect company shares one or more medium or strong signals with an existing client, the client name is added to the output under the "Matched Client" column.

This helps identify prospects that resemble current customers based on technology adoption patterns.

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

## Existing Client Analysis

A helper module (`client_extractor.py`) analyzes existing client websites and extracts relevant AI infrastructure signals.

The extracted signals are stored in memory and are used during the ICP discovery process to identify overlaps between prospects and existing customers.

Only medium and strong signals are considered for client matching.

---

## Output

The final spreadsheet contains:

| Column |
|----------|
| Company Name |
| Signal Found |
| Why It Suggests Buying Intent |
| Score |
| Matched Client |
| Source URL |

Example:

| Company Name | Signal Found | Why It Suggests Buying Intent | Score | Matched Clients | Source URL |
|-------------|-------------|--------|
| Example AI | llm, rag, vllm | Company appears to be building production-grade LLM... | 30 | Higgsfield, Sanas, ... | www.... |

---

## Project Components

Main Files:

- SignalScraper.py
- client_extractor.py

Input Files:

- output/companies.csv
- output/client_companies.csv

Generated Output:

- output/icp_signals_output.xlsx

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

Client input file:
output/client_companies.csv

Client matching:
Medium and Strong signals only

Generated output includes:
Matched Client column

---


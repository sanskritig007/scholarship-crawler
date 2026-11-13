# Atlas Scholarship Intelligence Engine

> **Edxso AI Engineer Intern — Assignment 2**  
> An autonomous, continuous intelligence engine that discovers, extracts, verifies, scores, and audits authentic scholarship opportunities for Indian students.

[![Tests](https://img.shields.io/badge/Tests-22%20Passed-success)](tests/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%203-lightgrey)](data/scholarships.db)
[![Demo Video](https://img.shields.io/badge/Demo%20Video-Google%20Drive-red?logo=googledrive)](https://drive.google.com/file/d/1jAfyCGAc9T-W_cY2MJQA8KfHO7TgaXuR/view?usp=sharing)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

> [!NOTE]
> ### 💡 Authorship, System Architecture & Engineering Ownership
> * **Conception, System Design & Problem Solving:** 100% conceived, architected, and directed by **Sanskriti Goswami**.
> * **AI Assistance Disclosure:** Generative AI was leveraged strictly as an accelerator for code synthesis, boilerplate generation, and rapid iteration under my constant instruction and review.
> * **Engineering Ownership:** Not a single architectural decision, schema field, or edge-case handling mechanism was decided autonomously by AI. Every idea—from the 4-pillar deterministic confidence rubric and verbatim sentence grounding to the third-party aggregator penalty, dual-portal URL distinction, and legacy government ASP.NET/IIS crash mitigations—came from my direct analysis of the assignment requirements and real-world portal constraints.

---

## 🎥 Demonstration Video Walkthrough

A complete end-to-end video demonstration explaining the system architecture, continuous crawler lifecycle, deterministic 4-pillar verification, verbatim evidence citations, and live dashboard walkthrough:

👉 **[Watch Live Video Demonstration (Google Drive)](https://drive.google.com/file/d/1jAfyCGAc9T-W_cY2MJQA8KfHO7TgaXuR/view?usp=sharing)**

---

## 🌟 Overview & Problem Statement

Built as the intelligence backbone for the **Atlas Funding** product prototype. Atlas normalizes educational funding opportunities into a universal schema and maintains repository freshness through continuous crawling.

This engine solves the assignment's core AI engineering challenge: **producing trustworthy, verifiable, hallucination-free outputs from unstructured internet documents** with complete provenance tracing:

$$\text{Database} \longrightarrow \text{Official Primary Source} \longrightarrow \text{Sentence Evidence} \longrightarrow \text{Extracted Value}$$

---

## 🏗️ Architecture & Pipeline Flow

The engine implements a continuous 7-stage autonomous lifecycle:

$$\text{Discover} \longrightarrow \text{Crawl} \longrightarrow \text{Extract} \longrightarrow \text{Verify} \longrightarrow \text{Score} \longrightarrow \text{Store} \longrightarrow \text{Update}$$

```
                          ┌───────────────────────────┐
                          │  Primary Seed Hubs        │
                          │  (Govt, CSR, Universities)│
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Discovery & Classifier   │
                          │  (Filters Aggregators)    │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Resilient Ingestion      │
                          │  (HTML & Text Parser)     │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Extraction & Grounding   │
                          │  (Verbatim Citation Map)  │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Deterministic Rubric     │
                          │  (4 Pillars, Max 100 pts) │
                          └─────────────┬─────────────┘
                                        │
                                        ▼
                          ┌───────────────────────────┐
                          │  Lifecycle & Audit Trail  │
                          │  (Corrigendum Diffs)      │
                          └─────────────┬─────────────┘
                                        │
                     ┌──────────────────┴──────────────────┐
                     ▼                                     ▼
         ┌───────────────────────┐             ┌───────────────────────┐
         │  SQLite Database      │             │  Enterprise Dashboard │
         │  (scholarships.db)    │             │  (Streamlit / Web UI) │
         └───────────────────────┘             └───────────────────────┘
```

---

## 🎯 Key Capabilities & Stand-Out Engineering

### 1. 🛡️ Anti-Hallucination & Evidence Grounding (PDF Section 5)
* **The Rule:** Never invent criteria. If family income limit is not stated on official primary sources, the system strictly outputs `"Not specified"` (never a hallucinated number like ₹5 Lakh).
* **Verbatim Citation:** Every crucial field (`deadline`, `amount`, `income_limit`) contains the exact quote extracted from the source document stored in the `evidence` JSON object.

### 2. 📊 Deterministic 100-Point Verification Rubric (PDF Section 4)
Critical rule strictly observed: **No arbitrary LLM confidence guessing**. The score is computed mathematically across 4 pillars:
* **Source Authority (30 pts):** Official Government `.gov.in` (30 pts); University `.ac.in` (28 pts); Corporate CSR (28 pts); Aggregators penalized (5 pts).
* **Evidence Grounding (30 pts):** Verified deadline match (+15 pts); Verified monetary benefit match (+15 pts).
* **Application Link Health (20 pts):** Live dedicated application/portal URL (+20 pts).
* **Temporal Recency & Session (20 pts):** Active 2026-27 intake deadline (+20 pts); Past deadline (+0 pts, marked `EXPIRED`).

> **Status Threshold:** $\ge 95.0\% \implies \textbf{VERIFIED / ACTIVE}$ | $< 95.0\% \implies \textbf{REVIEW REQUIRED}$

### 3. ⚡ Continuous Crawling & Change Detection (PDF Section 6 & 7)
* **Zero Blind Overwriting:** When rerun (Run 2), the engine detects field-level deltas (deadlines extended, revised grants).
* **Audit Trail (`scholarship_history`):** Preserves `old_value`, `new_value`, `detected_at`, `source_url`, and the source corrigendum snippet.

### 4. 🇮🇳 Real Multi-Category Indian Dataset (PDF Section 11)
Contains **24 authentic opportunities** spanning:
* **Government:** National Scholarship Portal (NSP), AICTE Pragati, AICTE Saksham, AICTE Swanath, UGC Ishan Uday, PM YASASVI, DST INSPIRE.
* **Corporate CSR:** Reliance Foundation (UG & PG), Tata Trusts, Infosys Foundation STEM Stars, HDFC Parivartan ECSS, L'Oréal India.
* **Universities:** IIT Bombay MCM, IIT Delhi Financial Assistance, Delhi University FSS, IIT Madras.
* **Foundations/Trusts:** KC Mahindra Education Trust, Sitaram Jindal Foundation.

---

## 🚀 Quickstart & Setup Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sanskritig007/scholarship-crawler.git
cd scholarship-crawler
```

### 2. Install Dependencies (100% Free & Open Source)
```bash
pip install -r requirements.txt
```
*(Note: The system also includes standard-library adapters so core tests and the dashboard server can run even with zero external packages installed!)*

---

## 💻 Running the System

### A. Run the Unit Test Suite (22 Comprehensive Tests)
```bash
PYTHONPATH=. python3 -m unittest discover tests -v
```
Verifies database integrity, change detection, domain classification, anti-hallucination grounding, confidence rubric, and edge cases.

### B. Run the Crawler Pipeline (Run 1 & Run 2)
```bash
PYTHONPATH=. python3 src/crawler.py
```
* **Run 1:** Ingests and normalizes 24 real scholarship records into `data/scholarships.db`.
* **Run 2:** Simulates policy corrigendums and captures change events in `scholarship_history`.

### C. Run the LLM Extraction & Anti-Hallucination Guardrail Demo
```bash
python3 demo_llm.py
```
Demonstrates how raw, messy government circulars are parsed by an LLM prompt and audited for zero hallucination.

### D. Launch the Interactive Dashboard

**Option 1: Official Streamlit Dashboard (PDF Section 10)**
```bash
streamlit run app/app.py
```

**Option 2: Zero-Dependency Instant Web Dashboard**
```bash
python3 app/server.py
```
Open your browser at 👉 **`http://localhost:8501`** (or `http://localhost:8502`).

---

## 📋 Evaluation Checklist & Deliverables

| Requirement (PDF Section 11 & 14) | Target | Achieved in Atlas |
| :--- | :---: | :---: |
| Real scholarship records | $\ge 20$ | **24 Real Indian Records** |
| Verified against primary/official sources | $\ge 15$ | **20 Verified** |
| High confidence ($\ge 95\%$) | $\ge 10$ | **20 Verified** |
| Source types represented | $\ge 3$ | **4 Categories (Govt, CSR, Univ, Trust)** |
| Change detection examples | $\ge 2$ | **2 Audited Corrigendums** |
| Expired / stale detection examples | $\ge 2$ | **2 Historical Schemes (NTSE, Lilavati)** |
| Free / Open-source tools only | 100% | **Zero Paid APIs or Scrapers Used** |
| Technical Note (3 pages max) | Included | [docs/technical_note.md](docs/technical_note.md) |

---

## 📁 Project Directory Structure

```text
scholarship-crawler/
│
├── data/
│   └── scholarships.db            # SQLite database file (inspectable)
│
├── src/
│   ├── config.py                  # Thresholds (95%), status constants, categories
│   ├── database.py                # Normalized schema (scholarships, history, runs)
│   ├── crawler.py                 # Multi-run orchestrator (Run 1 & Run 2)
│   │
│   ├── discovery/
│   │   ├── finder.py              # Seed-based opportunity discovery engine
│   │   └── classifier.py          # Domain authority & TLD classifier (.gov, .ac, CSR)
│   │
│   ├── scraper/
│   │   └── fetcher.py             # Dual-mode HTTP client (requests + urllib fallback)
│   │
│   ├── extraction/
│   │   ├── extractor.py           # Structured schema parser & entity extractor
│   │   ├── grounding.py           # Verbatim sentence citation & anti-hallucination
│   │   └── llm_extractor.py       # LLM extraction & AI guardrail auditor
│   │
│   ├── verification/
│   │   ├── scorer.py              # Deterministic 4-pillar 100-point rubric
│   │   └── validator.py           # Status assigner (ACTIVE vs REVIEW_REQUIRED)
│   │
│   └── lifecycle/
│       └── change_detector.py     # Delta calculator & audit history logger
│
├── app/
│   ├── app.py                     # Official Streamlit Dashboard (Section 10)
│   └── server.py                  # Zero-dependency browser UI studio
│
├── docs/
│   └── technical_note.md          # 3-Page Technical Evaluation Document
│
├── tests/
│   ├── test_database.py           # Database CRUD & audit trail tests
│   ├── test_discovery.py          # Domain classification tests
│   ├── test_extraction.py         # Anti-hallucination grounding tests
│   ├── test_verification.py       # Confidence rubric & score tests
│   └── test_edge_cases.py         # Edge cases & distinct links tests
│
├── demo.py                        # Live interactive CLI demo
├── demo_llm.py                    # Live LLM extraction & guardrail demo
├── requirements.txt               # Open source dependencies
└── README.md                      # Comprehensive guide & evaluation documentation
```

---

## 💡 Author's Engineering Insights, Edge Cases & Design Contributions

While architecting, implementing, and stress-testing this intelligence engine, I proactively identified several critical real-world edge cases and design considerations to ensure the system is genuinely production-ready, trustworthy, and resilient:

### 1. "Guaranteeing 100% Authentic Opportunities & Penalizing Aggregators"
* **My Insight:** I observed that relying on aggregators (like Buddy4Study or career blogs) often introduces outdated criteria and expired links. 
* **Design Decision:** I implemented an **Authoritative Seed Whitelist** prioritizing primary TLDs (`.gov.in`, `.nic.in`, `.ac.in`, and verified corporate foundations like Reliance, Tata, Infosys, and HDFC). I engineered an automatic penalty for third-party aggregator domains (capping them at 5/30 authority points), ensuring they **never cross the 95% threshold** and are always routed to `REVIEW REQUIRED` per PDF Section 2.

### 2. "Defining the True Role of AI Engineering vs Traditional Web Scraping"
* **My Insight:** I wanted to clearly separate brute-force web-scraping from authentic AI Engineering. Traditional scrapers break whenever CSS/DOM classes change, while raw LLMs frequently hallucinate eligibility rules.
* **Design Decision:** I structured the AI layer into 4 distinct pillars:
  * **Unstructured NLP Extraction:** Parsing messy gazettes, PDFs, and university circulars into a normalized 18-field schema.
  * **Zero-Hallucination Guardrails:** Verbatim sentence citation matching. If a source document does not mention an income ceiling, the engine strictly outputs `"Not specified"`, never inventing a number like ₹5 Lakh.
  * **Semantic Corrigendum Intelligence:** Distinguishing between initial announcements and policy amendments/extensions.
  * **Calibrated Verification:** Designing a deterministic 4-pillar evidence formula instead of relying on uncalibrated LLM confidence tokens.

### 3. "Architecting Distinct Primary Notification URLs vs Direct Application Portals"
* **My Insight:** During testing, I noticed that students often encounter two separate URLs: one where official circulars/guidelines are published, and another where the actual application form is submitted.
* **Design Decision:** I modeled both fields independently in the database:
  * **Official Source URL:** The authoritative policy/guidelines page (e.g. AICTE Pragati guidelines).
  * **Application URL:** The direct national/institutional submission portal (e.g. National Scholarship Portal `scholarships.gov.in`, Tata Trusts `onlinems.tatatrusts.org`, or IIT Bombay `asc.iitb.ac.in`).
  * **Adaptive UX:** I designed the UI to dynamically inspect both URLs: displaying two specialized action buttons when separate portals exist, and seamlessly collapsing into a single primary portal button when a single root applies.

### 4. "Handling Portal-Specific Routing & Legacy Government Portal Quirks (e.g. ASP.NET/IIS)"
* **My Insight:** While live-testing links in the browser (such as DST INSPIRE `online-inspire.gov.in`), I discovered that legacy Indian government portals run on ASP.NET/IIS architectures that throw session/cookie errors (`This website is too busy...`) when subpaths like `/apply` are requested directly without a prior session.
* **Design Decision:** I engineered the crawler to normalize application URLs to verified live entrypoints (e.g., the portal's verified root/registration flow), completely eliminating runtime browser crashes for students.

### 5. "Non-Destructive Continuous Crawling & Corrigendum Audit Trails (Run 1 vs Run 2)"
* **My Insight:** Scholarships are not static; deadlines get extended via corrigendum notifications. A standard database design would simply overwrite the old deadline with `UPDATE scholarships SET deadline = ...`, erasing critical history.
* **Design Decision:** I implemented an **Event-Sourced Audit Trail** (`scholarship_history` table). When Run 2 detects a change (e.g., NSP deadline extended from 31 Dec 2026 to 15 Jan 2027), the engine preserves the previous value, the new value, the timestamp, and the exact corrigendum sentence snippet as evidence.

---

## 👤 Author
**Sanskriti Goswami**  
Candidate for Edxso AI Engineer Intern  
Repository: [github.com/sanskritig007/scholarship-crawler](https://github.com/sanskritig007/scholarship-crawler)  
Demo Video: [Watch on Google Drive](https://drive.google.com/file/d/1jAfyCGAc9T-W_cY2MJQA8KfHO7TgaXuR/view?usp=sharing)


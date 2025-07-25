# 🧠 SKG Metadata Analysis

This repository supports the study presented in:

> **"Are Scientific Tasks and Methods Consistently Represented across Science Knowledge Graphs?"**  
> Jenifer Tabita Ciuciu-Kiss  
> Accepted at **Sci-K @ ISWC 2025**

We investigate whether category annotations (such as tasks and methods) for AI-related publications are consistently represented across multiple **Scientific Knowledge Graphs (SKGs)**, including:
- **Papers with Code**
- **OpenAlex**
- **OpenAIRE**
- **ORKG**

---

## 📁 Project Structure

.
├── data/
│ ├── data.json # Automatically created metadata (raw SKG annotations)
│ ├── all_data.json # Intermediate merged version
│ ├── initial_dataset.json # Cleaned and unified dataset (auto-generated)
│ └── gold_standard.json # Manually curated annotations (ground truth)
│
├── src/
│ ├── get_papers_with_code_categories.py
│ ├── get_openalex_categories.py
│ ├── get_openaire_categories.py
│ └── integrate_all_3_souces.py
│
├── get_initial_dataset.ipynb # Creates initial_dataset.json from data.json
├── analysis_initial_golden.ipynb # Analysis comparing initial vs. gold-standard
├── analysis_initial_golden.pdf # Final Sci-K 2025 paper
└── README.md


---

## ⚙️ Pipeline Overview

### 🔹 Step 1: Extract Raw Annotations

Scripts in `src/` pull annotations from each SKG and populate `data/data.json`:

- `get_papers_with_code_categories.py`  
  → Extracts tasks and methods from the Papers with Code JSON dump.

- `get_openalex_categories.py`  
  → Retrieves concept labels assigned by OpenAlex.

- `get_openaire_categories.py`  
  → Maps papers to OpenAIRE’s OECD FOS labels using metadata.

- `integrate_all_3_souces.py`  
  → Combines all three outputs into a single paper-centric structure.

### 🔹 Step 2: Clean and Aggregate

- Run `get_initial_dataset.ipynb`  
  → Cleans terminology, removes duplicates, and produces `initial_dataset.json`  
  (This is your **automatic baseline dataset**.)

### 🔹 Step 3: Gold Standard Curation

- `gold_standard.json`  
  → Manually reviewed annotations created to validate the auto-extracted results.

### 🔹 Step 4: Evaluation & Analysis

- Run `analysis_initial_golden.ipynb`  
  → Compares both datasets to assess precision, recall, agreement, and category overlap.

---

## 📊 Key Results (from the Paper)

Our comparative analysis revealed:

| SKG         | Precision | Recall | F1-score |
|-------------|-----------|--------|----------|
| PwC         | 0.42      | 0.23   | 0.30     |
| OpenAlex    | 0.33      | 0.35   | 0.34     |
| OpenAIRE    | 0.19      | 0.25   | 0.21     |
| ORKG        | 0.38      | 0.15   | 0.21     |

**Notable findings:**
- **PwC** annotations had the best overall precision.
- **OpenAlex** had the highest recall but suffered from label inflation.
- **Overlap between SKGs is low** — only 8 categories appeared in all four SKGs.
- **Terminological inconsistency** (e.g., `"NER"` vs `"Named Entity Recognition"`) and **granularity mismatches** were frequent.

> 🟠 These results highlight that existing SKGs diverge significantly in how they annotate scientific tasks/methods, raising challenges for automated classification and semantic interoperability.

---

## 📁 Dataset Description

Each paper entry includes:

```json
{
  "title": "...",
  "doi": "...",
  "abstract": "...",
  "papers_with_code_categories_flat": [...],
  "openalex_categories_flat": [...],
  "openaire_categories_flat": [...],
  "orkg_categories_flat": [...]
}
```


## 📄 License

This project is licensed under the Apache License 2.0.
You may obtain a copy of the license at:

http://www.apache.org/licenses/

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an “AS IS” BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
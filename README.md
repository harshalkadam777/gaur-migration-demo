Here’s a **fresh `README.md`** you can drop straight into your GitHub repo (`harshalkbison`). It’s structured so visitors understand the purpose, how to use it, and how to contribute:

---

# 🦬 Indian Gaur Migration — Konkan (2018–2024)

This repository hosts the complete study on **Indian Gaur (Bos gaurus) migration across the Konkan region of Maharashtra, India**, covering the period **2018–2024**.
It consolidates field reports, social media sightings (English + Marathi), and integrates environmental overlays for a holistic view of gaur movement.

---

## 📌 Project Highlights

* **6 years of data (2018–2024)** — cleaned, deduplicated, bilingual (English & Marathi sources).
* **Overlays integrated**:

  * 🌍 **Seismology** — National Center for Seismology (NCS) events
  * 💧 **Groundwater** — Central Ground Water Board (CGWB) weekly levels
  * 🌳 **Forest Cover** — NDVI data from ISRO/Bhuvan
* **Deliverables**:

  * Bilingual **Report (PDF)** + **Presentation (PPTX)**
  * Cleaned & enriched **Datasets (CSV/XLSX)**
  * Interactive **Maps (HTML)**
  * Streamlit **Dashboard App**
* **Automation**:

  * Weekly GitHub Actions pipeline
  * Anomaly detection & alerts (Slack / Issues)

---

## 📂 Repository Structure

```
/reports/      -> Final PDF & PPTX (bilingual)
/data/
   /processed/ -> Cleaned & enriched datasets
/maps/         -> Interactive Folium maps (HTML)
/figures/      -> Trend charts & overlays
/app/          -> Streamlit dashboard app
.github/workflows/ -> CI/CD for weekly updates
requirements.txt   -> Dependencies
README.md          -> This file
```

---

## 📊 Data Dictionary (key files)

* `sightings_clean_2018-2024.csv` — deduplicated sightings dataset
* `sightings_enriched_env_2018-2024.csv` — sightings with NDVI, groundwater, seismic overlays
* `weekly_counts_by_district.csv` — district-level weekly aggregates
* `weekly_env_overlays.csv` — weekly environmental indicators

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/harshalkadam777/harshalkbison.git
cd harshalkbison
```

### 2. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run the Streamlit dashboard

```bash
streamlit run app/streamlit_app.py
```

---

## 🌐 Live Access

* **GitHub Repo:** [harshalkadam777/harshalkbison](https://github.com/harshalkadam777/harshalkbison)
* **Streamlit Dashboard:** *(to be added after deployment)*
* **GitHub Pages (Maps):** *(if enabled, will host HTML maps here)*

---

## 📜 License

This project is released under the **MIT License**.
Please cite appropriately when using the datasets or visuals.

---

## 🙌 Acknowledgements

* National Center for Seismology (NCS)
* Central Ground Water Board (CGWB)
* ISRO Bhuvan (NDVI datasets)
* Citizen reporters across Konkan (English & Marathi posts)

# Measles Situation — Epidemiological Analysis (2026)

A reproducible, data-driven epidemiological study of the 2026 measles situation across two countries: **Bangladesh** and the **United States**.

---

## Repository Structure

```
Measles_Situation/
├── bangladesh/
│   ├── data/
│   │   ├── raw/
│   │   │   ├── data M new.xlsx            # Original source data (3 sheets)
│   │   │   └── dghs_daily_updates.csv    # DGHS daily outbreak totals (append new rows here)
│   │   ├── processed/
│   │   │   ├── measles_bangladesh_consolidated.xlsx   # 8-sheet consolidated dataset
│   │   │   └── update_log.txt             # Rebuild timestamps
│   │   └── bgd_adm_bbs_20201113_shp/     # BBS 2020 administrative shapefiles
│   ├── figures/                           # 18 publication-quality PNGs (300 DPI)
│   ├── publication/                       # 4 Lancet-ready choropleth maps
│   ├── scripts/
│   │   ├── build_dataset.py               # Dataset builder (WHO GHO API + raw data)
│   │   ├── fetch_dghs_update.py           # Scrapes BSS News for latest DGHS figures
│   │   ├── generate_lancet_maps.py        # Generates publication choropleth maps
│   │   └── run_pipeline.sh                # Full pipeline: fetch → build → execute notebook
│   └── measles_bangladesh_eda.ipynb       # Main analysis notebook (3 parts, 18 figures)
├── usa/
│   ├── data/
│   │   ├── measles_county_all_updates.csv # Johns Hopkins county-level case data
│   │   ├── processed_data_summary.csv     # State-level summary (generated)
│   │   └── Top_states_time_series.csv     # Top-state weekly series
│   ├── figures/                           # 4 publication-quality PNGs (300 DPI)
│   └── scripts/
│       └── make_figures.py                # Generates all 4 USA figures
├── manuscripts/                           # Drafts (Lancet.docx)
├── references/                            # Reference PDFs
├── requirements.txt                       # Python dependencies
├── setup.sh                               # One-shot environment setup
└── .github/workflows/update_data.yml      # GitHub Actions: daily Bangladesh data update
```

---

## Bangladesh Analysis (2000–2026)

A three-era study of measles burden and vaccination coverage:

- **MCV1 era (2000–2011):** coverage trends, immunity gap, and Rₜ estimation
- **MCV2 era (2012–2025):** dual-dose rollout, administrative overcounting, cases averted
- **2026 outbreak:** division and district choropleth maps, case cascade, age-stratified mortality, pairplots

### Data Sources

| Source | Indicator | Years |
|--------|-----------|-------|
| WHO GHO | Measles reported cases (`WHS3_62`) | 1975–2024 |
| WHO GHO | MCV1 coverage (`WHS8_110`) | 2000–2024 |
| WHO GHO | MCV2 coverage (`MCV2`) | 2012–2024 |
| DGHS Bangladesh | 2026 outbreak surveillance | Jan–May 2026 |
| BBS 2020 | Administrative shapefiles (divisions) | 2020 |

### Consolidated Workbook Sheets

| Sheet | Contents |
|-------|----------|
| `cases_full` | WHO GHO reported cases, 1975–2024 |
| `mcv1_coverage` | MCV1 coverage by source (WHO, Official, Admin), 2000–2025 |
| `mcv2_coverage` | MCV2 coverage by source, 2012–2025 |
| `outbreak_2026_summary` | National-level outbreak metrics |
| `outbreak_2026_divisions` | 8-division aggregation: cases, deaths, CFR |
| `outbreak_2026_districts` | 60-district breakdown |
| `outbreak_2026_timeseries` | Daily DGHS cumulative totals with CFR trend |
| `update_log` | Rebuild timestamps |

### Figures (Bangladesh)

| Figure | Description |
|--------|-------------|
| fig01 | Choropleth — 2026 cases by division |
| fig02 | Choropleth — 2026 CFR (%) by division |
| fig03 | Choropleth — 2026 incidence per 100,000 by division |
| fig04 | 2026 case cascade: suspected → hospitalised → confirmed → deaths |
| fig05 | 2026 age distribution of deaths |
| fig06 | 2026 cases and CFR by division (horizontal bars) |
| fig07 | PairGrid — 2026 district outbreak variables |
| fig08 | MCV1 coverage (3 sources) and annual cases — MCV1 era |
| fig09 | Immunity gap vs. measles burden |
| fig10 | Effective reproduction number Rₜ (2000–2025) |
| fig11 | MCV1 and MCV2 coverage — MCV2 era |
| fig12 | Coverage source discrepancy (admin vs. official vs. WHO) |
| fig13 | Cases + incidence rate with policy milestones (2000–2025) |
| fig14 | Era comparison boxplot (Mann–Whitney U) |
| fig15 | Cases averted by MCV2 — counterfactual log-linear analysis |
| fig16 | Estimated vaccination gap — cumulative unprotected children |
| fig17 | Pearson correlation heatmap — cases vs. MCV1/MCV2 |
| fig18 | Log-linear OLS regression — log₁₀(Cases) vs. coverage |

### Updating 2026 Outbreak Data

DGHS does not publish a machine-readable API. Figures are released through daily press briefings. To update:

1. Open `bangladesh/data/raw/dghs_daily_updates.csv`
2. Append a row:
   ```
   2026-05-19,28000,4100,,200,42,60,DGHS daily briefing
   ```
   Columns: `Date, Suspected_Cases, Confirmed_Cases, Hospitalised, Suspected_Deaths, Confirmed_Deaths, Districts_Affected, Source`
3. Leave unknown columns blank — the script handles `NaN` gracefully
4. Run `venv/bin/python bangladesh/scripts/build_dataset.py` to rebuild

---

## USA Analysis (2026)

Four publication-quality figures for a measles letter on the 2026 U.S. outbreak:

| Figure | Description |
|--------|-------------|
| figure1A | U.S. choropleth map — lab-confirmed cases by state (with AK/HI insets) |
| figure1B | Top 10 states — horizontal bar chart of cumulative cases |
| figure1C | State × week heatmap — weekly case intensity for top 10 states |
| figure1D | Kindergarten MMR coverage trend (2019–20 to 2024–25) vs. 95% threshold |

**Data source:** Johns Hopkins CSSEGISandData `measles_county_all_updates.csv`; CDC SchoolVaxView for MMR coverage.

Run:
```bash
venv/bin/python usa/scripts/make_figures.py
```

Figures are saved to `usa/figures/`. A state-level summary CSV is written to `usa/data/processed_data_summary.csv`.

---

## Setup and Reproduction

### Prerequisites

Install system LaTeX (required for Bangladesh figure text rendering) and GDAL/PROJ (for GeoPandas):

```bash
# Ubuntu / Debian
sudo apt install texlive-latex-extra texlive-fonts-recommended cm-super libgdal-dev libproj-dev
```

### Quick start

```bash
git clone <repo-url>
cd Measles_Situation
bash setup.sh
```

`setup.sh` will:
1. Verify Python 3.13+
2. Create a `venv/` virtual environment
3. Install all dependencies from `requirements.txt`
4. Register the `measles-bd` Jupyter kernel
5. Fetch fresh WHO GHO data and build the consolidated Bangladesh dataset

### Run the Bangladesh notebook

```bash
# Interactive
venv/bin/jupyter notebook bangladesh/measles_bangladesh_eda.ipynb

# Headless
venv/bin/jupyter nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=360 \
    --ExecutePreprocessor.kernel_name=measles-bd \
    bangladesh/measles_bangladesh_eda.ipynb \
    --output bangladesh/measles_bangladesh_eda.ipynb
```

### Manual setup

```bash
python3.13 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python -m ipykernel install --user --name measles-bd --display-name "Python 3.13 (measles-bd)"
venv/bin/python bangladesh/scripts/build_dataset.py
```

---

## Automated Data Updates (Bangladesh)

`bangladesh/scripts/build_dataset.py` runs automatically on weekdays via GitHub Actions and rebuilds the consolidated dataset from two sources:

```
WHO GHO API  ──→  build_dataset.py  ──→  consolidated .xlsx
                        ↑
             bangladesh/data/raw/dghs_daily_updates.csv
```

The workflow also runs `fetch_dghs_update.py` first to scrape the latest DGHS briefing from BSS News and append a new row to the CSV automatically.

---

## Requirements

| Package | Version |
|---------|---------|
| Python | ≥ 3.13 |
| pandas | ≥ 3.0 |
| numpy | ≥ 2.0 |
| matplotlib | ≥ 3.10 |
| seaborn | ≥ 0.13 |
| scipy | ≥ 1.17 |
| geopandas | ≥ 1.1 |
| openpyxl | ≥ 3.1 |
| requests | ≥ 2.33 |
| Pillow | ≥ 10.0 |
| ipykernel | ≥ 6.0 |
| nbconvert | ≥ 7.0 |

System: LaTeX (TeX Live 2023+), GDAL/PROJ (for GeoPandas)

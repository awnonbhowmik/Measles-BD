# Measles in Bangladesh — Epidemiological Analysis (2000–2026)

A reproducible, data-driven epidemiological study of measles burden and vaccination coverage in Bangladesh, covering three distinct analytical periods: the MCV1-only era (2000–2011), the MCV2 era (2012–2025), and the ongoing 2026 outbreak.

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Structure](#repository-structure)
3. [Data Sources](#data-sources)
4. [Analysis Structure](#analysis-structure)
5. [Figures](#figures)
6. [Setup and Reproduction](#setup-and-reproduction)
7. [Automated Data Updates](#automated-data-updates)
8. [Requirements](#requirements)

---

## Overview

Bangladesh introduced the first dose of the measles-containing vaccine (MCV1) into its national immunisation programme in 1979, and added a second dose (MCV2) in 2012. Despite achieving WHO-reported MCV1 coverage above 90% for most of the 2000s, measles outbreaks have continued — most dramatically in 2026, when more than 12,000 suspected cases and 166 deaths were reported in a single outbreak.

This study uses WHO Global Health Observatory (GHO) surveillance data alongside official Bangladeshi government sources to:

- Quantify the impact of MCV1 introduction and scale-up (2000–2011)
- Assess the added benefit — and continuing gaps — from MCV2 (2012–2025)
- Characterise the 2026 outbreak epidemiology by division, age group, and clinical severity
- Estimate the cumulative susceptibility pool built up through imperfect vaccination coverage
- Identify spatial and epidemiological risk patterns using division-level choropleth maps and statistical analysis

All figures are produced at 300 DPI using full LaTeX rendering for publication quality.

---

## Repository Structure

```
Measles-BD/
├── data/
│   ├── raw/
│   │   └── data M new.xlsx            # Original source data (3 sheets)
│   ├── processed/
│   │   ├── measles_bangladesh_consolidated.xlsx   # 7-sheet consolidated dataset
│   │   └── update_log.txt             # Rebuild timestamps
│   └── bgd_adm_bbs_20201113_shp/     # BBS 2020 administrative shapefiles
│       └── bgd_adm_bbs_20201113_SHP/
│           ├── bgd_admbnda_adm1_bbs_20201113.shp  # Division boundaries (8)
│           └── bgd_admbnda_adm2_bbs_20201113.shp  # District boundaries (64)
├── scripts/
│   └── build_dataset.py               # Dataset builder (WHO GHO API + raw data)
├── figures/                           # 18 publication-quality PNG figures (300 DPI)
│   ├── fig01_2026_division_cases_map.png
│   ├── fig02_2026_division_cfr_map.png
│   ├── fig03_2026_division_incidence_map.png
│   ├── fig04_2026_case_cascade.png
│   ├── fig05_2026_age_deaths.png
│   ├── fig06_2026_division_burden.png
│   ├── fig07_2026_pairplot.png
│   ├── fig08_mcv1_era_overview.png
│   ├── fig09_mcv1_immunity_gap.png
│   ├── fig10_rt_model.png
│   ├── fig11_mcv2_era_coverage.png
│   ├── fig12_coverage_source_gap.png
│   ├── fig13_cases_incidence_milestones.png
│   ├── fig14_era_comparison_boxplot.png
│   ├── fig15_cases_averted.png
│   ├── fig16_vaccination_gap.png
│   ├── fig17_correlation_heatmap.png
│   └── fig18_regression_coverage_cases.png
├── measles_bangladesh_eda.ipynb       # Main analysis notebook (3 parts, 18 figures)
├── .github/
│   └── workflows/
│       └── update_data.yml            # GitHub Actions: daily automated update
├── venv/                              # Python 3.13 virtual environment
└── README.md
```

---

## Data Sources

| Source | Indicator | Years | URL |
|--------|-----------|-------|-----|
| WHO GHO | Measles reported cases (`WHS3_62`) | 1975–2024 | [GHO API](https://ghoapi.azureedge.net/api/WHS3_62) |
| WHO GHO | MCV1 immunisation coverage (`WHS8_110`) | 2000–2024 | [GHO API](https://ghoapi.azureedge.net/api/WHS8_110) |
| WHO GHO | MCV2 immunisation coverage (`MCV2`) | 2012–2024 | [GHO API](https://ghoapi.azureedge.net/api/MCV2) |
| DGHS Bangladesh | 2026 outbreak surveillance (hospital-based) | Jan–Apr 2026 | [DGHS Press Releases](https://dghs.gov.bd/views/latest-news) |
| BBS 2020 | Administrative shapefiles (divisions & districts) | 2020 | National shapefile |

### Consolidated Workbook Sheets

| Sheet | Contents |
|-------|----------|
| `cases_full` | WHO GHO reported cases, 1975–2024 |
| `mcv1_coverage` | MCV1 coverage by source (WHO, Official, Admin), 2000–2025 |
| `mcv2_coverage` | MCV2 coverage by source (WHO, Official, Admin), 2012–2025 |
| `analysis_merged` | Combined coverage + cases for modelling, 2000–2025 |
| `outbreak_2026_summary` | National-level outbreak metrics (13 key indicators) |
| `outbreak_2026_divisions` | 8-division aggregation: cases, deaths, CFR |
| `outbreak_2026_districts` | 60-district breakdown with division label |
| `update_log` | ISO-format rebuild timestamps |

---

## Analysis Structure

The notebook (`measles_bangladesh_eda.ipynb`) is organised into three fully separate parts — no era mixing:

### Part III — 2026 Outbreak (presented first — demographic context)

- Division choropleth maps with compass rose and scale bar (raw cases, CFR, incidence rate per 100,000)
- Case cascade: suspected → hospitalised → lab-confirmed → deaths
- Age-stratified mortality: 92.9% of deaths in children under 18
- Division-level burden (cases and CFR) as bar charts
- Pairplot of district-level outbreak variables (Cases, Deaths, CFR, log-scales)
- **Figures:** fig01–07

### Part I — MCV1 Era (2000–2011)

- MCV1 coverage trends across three data sources (WHO, Official/Survey, Administrative)
- Correlation between coverage gaps and annual case burden
- Immunity gap model: coverage below 95% (herd immunity threshold for measles R₀ ≈ 12–18)
- Effective reproduction number Rₜ estimated from coverage each year
- **Figures:** fig08–10

### Part II — MCV2 Era (2012–2025)

- MCV1 and MCV2 coverage side-by-side across all sources
- Administrative overcounting: admin coverage >100% indicates denominator inflation
- Source discrepancy analysis (admin vs. WHO vs. official)
- Annual cases + incidence rate (per 100,000) with policy milestones
- Era comparison (Mann–Whitney U test): MCV1-only vs. MCV2 era
- Cases averted by MCV2: log-linear counterfactual analysis
- Cumulative susceptibility model: estimated unprotected children, 2012–2025
- **Figures:** fig11–16

### Statistical Analysis (Cross-Era)

- Pearson correlation heatmap: measles cases vs. MCV1/MCV2 coverage (2000–2026)
- Log-linear OLS regression: log₁₀(Cases) ~ MCV1 and MCV2 WHO coverage
- **Figures:** fig17–18

---

## Figures

| Figure | Description |
|--------|-------------|
| fig01 | **Choropleth map** — 2026 cases by division (YlOrRd, compass rose, scale bar) |
| fig02 | **Choropleth map** — 2026 CFR (%) by division (YlOrRd, compass rose, scale bar) |
| fig03 | **Choropleth map** — 2026 incidence rate per 100,000 by division (BBS 2022 census pop.) |
| fig04 | 2026 outbreak case cascade — absolute counts and % of suspected cases |
| fig05 | 2026 outbreak — age distribution of deaths (bar + donut) |
| fig06 | 2026 outbreak — cases and CFR by division (horizontal bars) |
| fig07 | **PairGrid** — 2026 district outbreak: scatter (upper), KDE contour (lower), KDE (diagonal) |
| fig08 | MCV1 coverage (3 sources) and annual cases — MCV1 era (2000–2011) |
| fig09 | Immunity gap vs. measles burden — bars in red when coverage < 95% |
| fig10 | Effective reproduction number Rₜ from coverage data (2000–2025); Rₜ = R₀ × (1 − p_eff) |
| fig11 | MCV1 and MCV2 coverage by source — MCV2 era (2012–2025) |
| fig12 | Coverage source discrepancy — administrative vs. official vs. WHO |
| fig13 | Measles cases + incidence rate (per 100,000) with policy milestones (2000–2025) |
| fig14 | Era comparison boxplot — MCV1-only vs. MCV2 era (Mann–Whitney U) |
| fig15 | Cases averted by MCV2 — counterfactual log-linear trend analysis (2012–2025) |
| fig16 | Estimated vaccination gap — annual and cumulative unprotected children (2012–2025) |
| fig17 | Pearson correlation heatmap — cases vs. MCV1/MCV2 coverage (2000–2026) |
| fig18 | Log-linear OLS regression — log₁₀(Cases) vs. MCV1 and MCV2 WHO coverage |

All figures use full LaTeX rendering (`text.usetex = True`) with the `amsmath` and `amssymb` packages.

---

## Setup and Reproduction

### Prerequisites

Install system LaTeX (required for figure text rendering) and GDAL/PROJ (for GeoPandas):

```bash
# Ubuntu / Debian
sudo apt install texlive-latex-extra texlive-fonts-recommended cm-super libgdal-dev libproj-dev
```

### Quick start (recommended)

Clone the repository, then run the included setup script — it handles everything automatically:

```bash
git clone <repo-url>
cd Measles-BD
bash setup.sh
```

`setup.sh` will:
1. Create a `venv/` virtual environment using Python 3.13
2. Install all dependencies from `requirements.txt`
3. Register the `measles-bd` Jupyter kernel
4. Fetch fresh data from WHO GHO and build the consolidated dataset

### Run the notebook

```bash
# Interactive
venv/bin/jupyter notebook measles_bangladesh_eda.ipynb

# Headless execution
venv/bin/jupyter nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=360 \
    --ExecutePreprocessor.kernel_name=measles-bd \
    measles_bangladesh_eda.ipynb \
    --output measles_bangladesh_eda.ipynb
```

### Manual setup (if preferred)

```bash
python3.13 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/python -m ipykernel install --user --name measles-bd --display-name "Python 3.13 (measles-bd)"
venv/bin/python scripts/build_dataset.py
```

---

## Automated Data Updates

A GitHub Actions workflow (`.github/workflows/update_data.yml`) runs automatically on weekdays at **06:00 UTC** (noon Bangladesh time, when WHO GHO typically updates):

```
┌─────────────────────┐
│  WHO GHO API        │──→ build_dataset.py ──→ consolidated .xlsx
│  (WHS3_62, WHS8_110,│                              │
│   MCV2)             │                              ↓
└─────────────────────┘                     commit & push to repo
```

The workflow:
1. Checks out the repository
2. Sets up Python 3.13
3. Installs all dependencies
4. Runs `scripts/build_dataset.py` (fetches fresh WHO data)
5. Attempts to execute the notebook via `papermill` (skips gracefully if kernel unavailable in CI)
6. Commits and pushes any changes to `data/processed/`

The workflow can also be triggered manually from the GitHub Actions UI via `workflow_dispatch`.

Each time the notebook runs, it reads the update timestamp from the `update_log` sheet and displays:

> **Data reflects: DD Month YYYY**

at the top of every output.

---

## Requirements

| Package | Version |
|---------|---------|
| Python | 3.13 |
| pandas | 3.0.2 |
| numpy | 2.4.4 |
| matplotlib | 3.10.8 |
| seaborn | 0.13.2 |
| scipy | 1.17.1 |
| geopandas | 1.1.3 |
| openpyxl | 3.1.5 |
| requests | 2.33.1 |
| ipykernel | ≥ 6.0 |
| papermill | ≥ 2.0 |
| nbconvert | ≥ 7.0 |

System: LaTeX (TeX Live 2023+), GDAL/PROJ (for GeoPandas)

#!/usr/bin/env python3
"""
make_figures.py
Generates four publication-quality PNG figures for a Science in One Health
Letter on measles in the United States in 2026.

Data sources:
  - Johns Hopkins CSSEGISandData: measles_county_all_updates.csv
  - CDC SchoolVaxView (kindergarten MMR coverage manually entered from
    CDC-reported values; see comments in Figure 1D section)
  - US states shapefile: Census Bureau TIGER/Line cb_2022_us_state_20m
"""

import sys
import os
import io
import zipfile
import warnings
import requests
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
import matplotlib.cm as mcm
from matplotlib.ticker import MaxNLocator
import geopandas as gpd
from PIL import Image

warnings.filterwarnings("ignore")

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(_SCRIPT_DIR, "..", "data")
FIG_DIR    = os.path.join(_SCRIPT_DIR, "..", "figures")

# ── Consistent visual style ────────────────────────────────────────────────────
FIG_W, FIG_H   = 6.5, 5.0
DPI            = 300
FONT_FAMILY    = "DejaVu Sans"
TITLE_SIZE     = 11
SUBTITLE_SIZE  = 8
LABEL_SIZE     = 9
TICK_SIZE      = 8
LEGEND_SIZE    = 8
ANNOT_SIZE     = 7
LINE_W         = 1.5

MAP_CMAP       = "YlOrRd"
HEAT_CMAP      = "YlOrRd"
BAR_COLOR      = "#3a6ea8"
MMR_LINE_COLOR = "#1f4e79"
TARGET_COLOR   = "#b22222"
NO_DATA_COLOR  = "#d9d9d9"

plt.rcParams.update({
    "font.family":       FONT_FAMILY,
    "font.size":         TICK_SIZE,
    "axes.titlesize":    TITLE_SIZE,
    "axes.titleweight":  "bold",
    "axes.labelsize":    LABEL_SIZE,
    "xtick.labelsize":   TICK_SIZE,
    "ytick.labelsize":   TICK_SIZE,
    "legend.fontsize":   LEGEND_SIZE,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         False,
    "figure.dpi":        DPI,
    "savefig.dpi":       DPI,
    "savefig.facecolor": "white",
    "axes.facecolor":    "white",
    "figure.facecolor":  "white",
})

SAVE_KW = dict(dpi=DPI, bbox_inches="tight", facecolor="white")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — Load county data, compute one shared DATE_MAX
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 62)
print("MEASLES FIGURES — PROCESSING SUMMARY")
print("=" * 62)

COUNTY_FILE = os.path.join(DATA_DIR, "measles_county_all_updates.csv")
df = pd.read_csv(COUNTY_FILE)
df["date"] = pd.to_datetime(df["date"])

# Single filter applied once: 2026-01-01 through latest record
df2026 = df[
    (df["date"] >= "2026-01-01") &
    (df["outcome_type"] == "case_lab-confirmed")
].copy()

DATE_MAX_DT  = df2026["date"].max()                      # datetime object
DATE_MAX_STR = DATE_MAX_DT.strftime("%Y-%m-%d")          # terminal / CSV
DATE_MAX_LBL = DATE_MAX_DT.strftime("%b. %-d")           # "May 8"  (figure subtitles)
DATE_RANGE_LBL = f"Jan. 1–{DATE_MAX_LBL}, 2026"    # "Jan. 1–May 8, 2026"

print(f"\n[Data] File      : {COUNTY_FILE}")
print(f"[Data] Filter    : outcome_type == 'case_lab-confirmed', 2026-01-01 onward")
print(f"[Data] DATE_MAX  : {DATE_MAX_STR}  ← used in all four figures")

# ── Parse state from "County/Region, State" ────────────────────────────────────
def parse_state(name: str) -> str:
    parts = name.rsplit(",", 1)
    return parts[1].strip() if len(parts) == 2 else "Unknown"

df2026["state"] = df2026["location_name"].apply(parse_state)

# ── State totals (single source of truth for 1A, 1B, 1C) ──────────────────────
state_totals = (
    df2026.groupby("state")["value"].sum()
    .sort_values(ascending=False)
)
TOP10 = state_totals.head(10).index.tolist()

print(f"\n[Result] Confirmed cases, {DATE_RANGE_LBL}: {int(state_totals.sum())} "
      f"across {len(state_totals)} states")
print(f"[Top 10 states]")
for i, (s, n) in enumerate(state_totals.head(10).items(), 1):
    print(f"  {i:2d}. {s:<22s}: {int(n)}")

# ── Weekly aggregation from county data (floor each date to Sunday) ────────────
df2026["week_start"] = (
    df2026["date"]
    - pd.to_timedelta((df2026["date"].dt.dayofweek + 1) % 7, unit="D")
)
weekly = (
    df2026.groupby(["state", "week_start"])["value"]
    .sum()
    .reset_index()
    .rename(columns={"value": "cases"})
)

# Heatmap pivot: top-10 states × all weeks in 2026
heat_pivot = (
    weekly[weekly["state"].isin(TOP10)]
    .pivot(index="state", columns="week_start", values="cases")
    .fillna(0)
    .loc[TOP10]          # keep highest-burden state at top row
)

print(f"\n[Heatmap] Weeks: {heat_pivot.columns.min().strftime('%Y-%m-%d')} "
      f"→ {heat_pivot.columns.max().strftime('%Y-%m-%d')}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — US states shapefile
# ══════════════════════════════════════════════════════════════════════════════
MAP_AVAILABLE = False
states_all_gdf = None   # all 50 states + DC
states_conus   = None
states_ak      = None
states_hi      = None

SHAPEFILE_DIR  = os.path.join(DATA_DIR, "temp_states")
SHAPEFILE_PATH = os.path.join(SHAPEFILE_DIR, "cb_2022_us_state_20m.shp")
SHAPEFILE_URL  = (
    "https://www2.census.gov/geo/tiger/GENZ2022/shp/cb_2022_us_state_20m.zip"
)

try:
    if not os.path.exists(SHAPEFILE_PATH):
        os.makedirs(SHAPEFILE_DIR, exist_ok=True)
        print(f"\n[Map] Downloading Census shapefile …")
        resp = requests.get(SHAPEFILE_URL, timeout=45)
        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code}")
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(SHAPEFILE_DIR)
        print("[Map] Downloaded and extracted.")

    raw = gpd.read_file(SHAPEFILE_PATH)
    # Exclude unincorporated territories only
    TERR_FIPS = {"60", "66", "69", "72", "78"}
    states_all_gdf = raw[~raw["STATEFP"].isin(TERR_FIPS)].copy()  # 50 + DC

    states_conus = states_all_gdf[
        ~states_all_gdf["STATEFP"].isin({"02", "15"})
    ]
    states_ak = states_all_gdf[states_all_gdf["STATEFP"] == "02"]
    states_hi = states_all_gdf[states_all_gdf["STATEFP"] == "15"]

    MAP_AVAILABLE = True
    print("[Map] Geographic choropleth ready — 50 states + DC; AK/HI as insets.")

except Exception as exc:
    print(f"\n[Map] Shapefile unavailable ({exc}). Tile map fallback will be used.")
    MAP_AVAILABLE = False

# ── Helper: merge case totals onto a GeoDataFrame ─────────────────────────────
state_df = state_totals.reset_index()
state_df.columns = ["state_name", "cases"]

def merge_cases(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    out = gdf.merge(state_df, left_on="NAME", right_on="state_name", how="left")
    out["cases"] = out["cases"].fillna(0)
    return out


# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1A — U.S. choropleth map with AK / HI insets
# ══════════════════════════════════════════════════════════════════════════════
print("\n--- Figure 1A: Map ---")

fig = plt.figure(figsize=(FIG_W, FIG_H))
# Main CONUS axes
ax = fig.add_axes([0.01, 0.17, 0.98, 0.74])   # [L, B, W, H] in figure fraction

SUBTITLE_1A = f"Cumulative laboratory-confirmed cases, {DATE_RANGE_LBL}"

if MAP_AVAILABLE:
    vmax = int(state_totals.max())
    norm = mcolors.Normalize(vmin=0, vmax=vmax)   # linear → equal tick spacing

    # ── CONUS ────────────────────────────────────────────────────────────────
    conus_m = merge_cases(states_conus).to_crs("ESRI:102003")
    conus_m.plot(
        column="cases", cmap=MAP_CMAP, norm=norm,
        linewidth=0.3, edgecolor="#666666",
        ax=ax, missing_kwds={"color": NO_DATA_COLOR},
    )
    ax.set_aspect("auto")
    x0, y0, x1, y1 = conus_m.total_bounds
    bx, by = (x1 - x0) * 0.01, (y1 - y0) * 0.01
    ax.set_xlim(x0 - bx, x1 + bx)
    ax.set_ylim(y0 - by, y1 + by)
    ax.set_axis_off()

    # ── State abbreviation labels ─────────────────────────────────────────────
    # Manual xy offsets (metres, Albers ESRI:102003) for small / crowded states.
    # Positive x = east, positive y = north.
    LABEL_OFFSETS = {
        "Massachusetts":  (  20000,  60000),
        "Rhode Island":   ( 130000,  20000),
        "Connecticut":    ( 120000, -50000),
        "New Jersey":     ( 120000,  20000),
        "Delaware":       ( 150000,  30000),
        "Maryland":       ( 120000, -60000),
        "West Virginia":  ( -20000, -20000),
        "District of Columbia": (0, 0),   # DC: skip (invisible at this scale)
    }
    SKIP_LABELS = {"District of Columbia"}

    for _, row in conus_m.iterrows():
        name = row["NAME"]
        if name in SKIP_LABELS:
            continue
        abbr = row["STUSPS"]
        pt   = row.geometry.representative_point()
        dx, dy = LABEL_OFFSETS.get(name, (0, 0))
        cx, cy = pt.x + dx, pt.y + dy

        # White text on dark-filled states, dark text on light ones
        brightness = norm(float(row["cases"]))
        txt_col    = "white" if brightness > 0.62 else "#333333"
        ax.text(cx, cy, abbr,
                ha="center", va="center",
                fontsize=5.5, fontweight="bold", color=txt_col,
                clip_on=True)

    # ── Alaska inset ──────────────────────────────────────────────────────────
    ax_ak = fig.add_axes([0.00, 0.17, 0.20, 0.18])
    ak_m = merge_cases(states_ak).to_crs("EPSG:3338")
    ak_m.plot(column="cases", cmap=MAP_CMAP, norm=norm,
              linewidth=0.3, edgecolor="#666666", ax=ax_ak,
              missing_kwds={"color": NO_DATA_COLOR})
    ax_ak.set_aspect("auto")
    ax_ak.set_axis_off()
    for sp in ax_ak.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.5); sp.set_color("#aaaaaa")
    ax_ak.set_title("AK", fontsize=6, pad=2)

    # ── Hawaii inset ──────────────────────────────────────────────────────────
    ax_hi = fig.add_axes([0.21, 0.17, 0.15, 0.11])
    hi_m = merge_cases(states_hi).to_crs("EPSG:4135")
    hi_m.plot(column="cases", cmap=MAP_CMAP, norm=norm,
              linewidth=0.3, edgecolor="#666666", ax=ax_hi,
              missing_kwds={"color": NO_DATA_COLOR})
    ax_hi.set_aspect("auto")
    ax_hi.set_axis_off()
    for sp in ax_hi.spines.values():
        sp.set_visible(True); sp.set_linewidth(0.5); sp.set_color("#aaaaaa")
    ax_hi.set_title("HI", fontsize=6, pad=2)

    # ── Colorbar ──────────────────────────────────────────────────────────────
    sm = plt.cm.ScalarMappable(cmap=MAP_CMAP, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.30, 0.09, 0.40, 0.022])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    # Explicit ticks that include the true maximum
    nice_ticks = list(range(0, vmax, 100)) + [vmax]
    cbar.set_ticks(nice_ticks)
    cbar.ax.tick_params(labelsize=TICK_SIZE - 1, pad=2)
    cbar.set_label("Confirmed cases", size=ANNOT_SIZE + 1, labelpad=3)

else:
    # ── Tile map fallback (unchanged from previous version) ───────────────────
    TILES = {
        "ME":(11,0),
        "WA":(0,1),"MT":(2,1),"ND":(4,1),"MN":(5,1),
        "WI":(6,1),"MI":(8,1),"VT":(10,1),"NH":(11,1),
        "OR":(0,2),"ID":(1,2),"WY":(3,2),"SD":(4,2),
        "IA":(5,2),"IL":(6,2),"IN":(7,2),"OH":(8,2),
        "PA":(9,2),"NY":(10,2),"MA":(11,2),"RI":(12,2),
        "CA":(0,3),"NV":(1,3),"UT":(2,3),"CO":(3,3),
        "NE":(4,3),"MO":(5,3),"KY":(6,3),"WV":(7,3),
        "VA":(8,3),"MD":(9,3),"DE":(10,3),"NJ":(11,3),"CT":(12,3),
        "AZ":(1,4),"NM":(2,4),"KS":(4,4),"AR":(5,4),
        "TN":(6,4),"NC":(7,4),"SC":(8,4),
        "TX":(3,5),"OK":(4,5),"LA":(5,5),"MS":(6,5),
        "AL":(7,5),"GA":(8,5),"FL":(9,5),
        "AK":(0,6),"HI":(1,6),
    }
    ABBREV = {
        "Alabama":"AL","Arizona":"AZ","Arkansas":"AR","California":"CA",
        "Colorado":"CO","Connecticut":"CT","Delaware":"DE","Florida":"FL",
        "Georgia":"GA","Hawaii":"HI","Idaho":"ID","Illinois":"IL",
        "Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY",
        "Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA",
        "Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO",
        "Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH",
        "New Jersey":"NJ","New Mexico":"NM","New York":"NY",
        "North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK",
        "Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI",
        "South Carolina":"SC","South Dakota":"SD","Tennessee":"TN",
        "Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA",
        "Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY",
        "Alaska":"AK",
    }
    state_cases = state_totals.to_dict()
    vmax     = int(state_totals.max())
    norm     = mcolors.Normalize(vmin=0, vmax=vmax)
    cmap_fn  = mcm.get_cmap(MAP_CMAP)
    ax.set_xlim(-0.5, 12.5); ax.set_ylim(6.5, -0.5)
    ax.set_aspect("equal"); ax.set_axis_off()
    for abbr, (col, row) in TILES.items():
        full   = next((k for k, v in ABBREV.items() if v == abbr), None)
        n      = state_cases.get(full, 0)
        colour = cmap_fn(norm(n)) if n > 0 else NO_DATA_COLOR
        rect   = mpatches.FancyBboxPatch(
            (col-0.45, row-0.45), 0.9, 0.9,
            boxstyle="round,pad=0.02",
            facecolor=colour, edgecolor="#888", linewidth=0.5)
        ax.add_patch(rect)
        tc = "white" if norm(n) > 0.55 else "#222"
        ax.text(col, row-0.1, abbr, ha="center", va="center",
                fontsize=5.5, fontweight="bold", color=tc)
        if n > 0:
            ax.text(col, row+0.28, str(int(n)), ha="center",
                    va="center", fontsize=4.5, color=tc)
    sm = plt.cm.ScalarMappable(cmap=MAP_CMAP, norm=norm)
    sm.set_array([])
    cbar_ax = fig.add_axes([0.30, 0.09, 0.40, 0.022])
    cbar = fig.colorbar(sm, cax=cbar_ax, orientation="horizontal")
    nice_ticks = list(range(0, vmax, 100)) + [vmax]
    cbar.set_ticks(nice_ticks)
    cbar.ax.tick_params(labelsize=TICK_SIZE - 1)
    cbar.set_label("Confirmed cases", size=ANNOT_SIZE + 1)

# Title + subtitle (applies regardless of map type)
fig.text(0.50, 0.96, "Measles cases by state in 2026",
         ha="center", va="top", fontsize=TITLE_SIZE, fontweight="bold")
fig.text(0.50, 0.91, SUBTITLE_1A,
         ha="center", va="top", fontsize=SUBTITLE_SIZE, color="#444444")

plt.savefig(os.path.join(FIG_DIR, "figure1A_map.png"), **SAVE_KW)
plt.close()
print("  Saved: figure1A_map.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1B — Top 10 states, horizontal bar chart
# ══════════════════════════════════════════════════════════════════════════════
print("--- Figure 1B: Bar chart ---")

top10_data = state_totals.head(10).iloc[::-1]   # reverse → highest at top

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

bars = ax.barh(top10_data.index, top10_data.values,
               color=BAR_COLOR, edgecolor="none", height=0.62)

for bar, val in zip(bars, top10_data.values):
    ax.text(val + top10_data.values.max() * 0.012,
            bar.get_y() + bar.get_height() / 2,
            str(int(val)), va="center", ha="left",
            fontsize=ANNOT_SIZE, color="#222222")

ax.set_xlabel("Laboratory-confirmed cases", fontsize=LABEL_SIZE)
# Title and subtitle via suptitle/text so they don't crowd each other
fig.suptitle("Top states by cumulative measles cases, 2026",
             fontsize=TITLE_SIZE, fontweight="bold", y=0.97)
fig.text(0.5, 0.91, DATE_RANGE_LBL,
         ha="center", va="top", fontsize=SUBTITLE_SIZE, color="#444444")

ax.set_xlim(0, top10_data.values.max() * 1.15)
ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "figure1B_top_states_bar.png"), **SAVE_KW)
plt.close()
print("  Saved: figure1B_top_states_bar.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1C — State × week heatmap (top 10 states, from county data)
# ══════════════════════════════════════════════════════════════════════════════
print("--- Figure 1C: Heatmap ---")

# heat_pivot: rows = top 10 states (high→low), columns = week_start datetimes
pivot    = heat_pivot.copy()
n_states = len(pivot)
n_weeks  = len(pivot.columns)

week_labels = [d.strftime("%-d %b") for d in pivot.columns]

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.subplots_adjust(left=0.22, right=0.93, top=0.87, bottom=0.22)

heat_vmax = pivot.values.max()
heat_norm = mcolors.Normalize(vmin=0, vmax=heat_vmax)   # linear → equal tick spacing
heat_cmap = mcm.get_cmap(HEAT_CMAP)
heat_cmap.set_under("#f7f7f7")   # near-zero weeks show as very light grey

# Draw cells with pcolormesh
# pcolormesh expects (n_states+1) × (n_weeks+1) edges for n_states × n_weeks cells
im = ax.pcolormesh(
    np.arange(n_weeks + 1),
    np.arange(n_states + 1),
    pivot.values,
    cmap=heat_cmap,
    norm=heat_norm,
    linewidth=0.4,
    edgecolors="#cccccc",
)

# Annotate cells with non-zero counts (only if ≥ 5 to avoid clutter)
for r, state in enumerate(pivot.index):
    for c, col in enumerate(pivot.columns):
        val = int(pivot.loc[state, col])
        if val >= 5:
            brightness = heat_norm(val)
            txt_color  = "white" if brightness > 0.60 else "#222222"
            ax.text(c + 0.5, r + 0.5, str(val),
                    ha="center", va="center",
                    fontsize=6, color=txt_color, fontweight="bold")

# y-axis: state names
ax.set_yticks(np.arange(n_states) + 0.5)
ax.set_yticklabels(
    [f"{s}  ({int(state_totals[s])})" for s in pivot.index],
    fontsize=TICK_SIZE - 1
)
ax.yaxis.tick_left()

# x-axis: week labels (rotated)
ax.set_xticks(np.arange(n_weeks) + 0.5)
ax.set_xticklabels(week_labels, rotation=45, ha="right", fontsize=TICK_SIZE - 2)

ax.set_xlim(0, n_weeks)
ax.set_ylim(0, n_states)
ax.invert_yaxis()          # top state at top row
ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)

# Colorbar
sm_h = plt.cm.ScalarMappable(cmap=heat_cmap, norm=heat_norm)
sm_h.set_array([])
cbar_h = fig.colorbar(sm_h, ax=ax, orientation="horizontal",
                       fraction=0.04, pad=0.18, shrink=0.7,
                       label="Weekly confirmed cases")
# Sparse ticks so labels don't crowd; always include 0 and actual max
heat_ticks = [0, 50, 100, 150, 200, int(heat_vmax)]
heat_ticks = sorted(set(heat_ticks))   # dedup if vmax is already a round number
cbar_h.set_ticks(heat_ticks)
cbar_h.ax.tick_params(labelsize=TICK_SIZE - 1)

fig.text(0.57, 0.96, "Weekly measles intensity in high-burden states, 2026",
         ha="center", va="top", fontsize=TITLE_SIZE, fontweight="bold")
fig.text(0.57, 0.915, DATE_RANGE_LBL + "  |  n = cumulative cases per state",
         ha="center", va="top", fontsize=SUBTITLE_SIZE, color="#444444")

plt.savefig(os.path.join(FIG_DIR, "figure1C_weekly_curves.png"), **SAVE_KW)
plt.close()
print("  Saved: figure1C_weekly_curves.png")

# ══════════════════════════════════════════════════════════════════════════════
# FIGURE 1D — Kindergarten MMR coverage (CDC SchoolVaxView)
# ══════════════════════════════════════════════════════════════════════════════
print("--- Figure 1D: MMR coverage ---")

# Values manually entered from CDC SchoolVaxView / MMWR annual kindergarten
# vaccination coverage surveys.  Source:
#   CDC SchoolVaxView: cdc.gov/schoolvaxview
#   MMWR Morb Mortal Wkly Rep — kindergarten vaccination coverage reports
MMR_DATA = {
    "2019–20": 95.2,
    "2020–21": 93.9,
    "2021–22": 93.0,
    "2022–23": 93.1,
    "2023–24": 92.7,
    "2024–25": 92.5,
}

school_years = list(MMR_DATA.keys())
coverage     = list(MMR_DATA.values())
x_pos        = np.arange(len(school_years))

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))

# 95% threshold line
ax.axhline(y=95.0, color=TARGET_COLOR, linewidth=1.5,
           linestyle="--", zorder=2, label="95% community-immunity threshold")

# Shaded gap — deliberately light (alpha=0.07)
ax.fill_between(x_pos, coverage, 95.0,
                where=[c < 95.0 for c in coverage],
                alpha=0.07, color=TARGET_COLOR)

# Coverage line
ax.plot(x_pos, coverage,
        color=MMR_LINE_COLOR, linewidth=LINE_W + 0.5,
        marker="o", markersize=5, zorder=3,
        label="National kindergarten MMR coverage")

# Point labels
for xi, cov in zip(x_pos, coverage):
    ax.text(xi, cov - 0.22, f"{cov:.1f}%",
            ha="center", va="top", fontsize=ANNOT_SIZE, color=MMR_LINE_COLOR)

ax.set_xticks(x_pos)
ax.set_xticklabels(school_years, rotation=30, ha="right", fontsize=TICK_SIZE)
ax.set_xlabel("School year", fontsize=LABEL_SIZE)
ax.set_ylabel("MMR coverage among kindergartners (%)", fontsize=LABEL_SIZE)
ax.set_ylim(91.5, 96.5)

ax.set_title("Kindergarten MMR coverage below the 95% target",
             fontsize=TITLE_SIZE, fontweight="bold", pad=4)
ax.legend(loc="lower left", frameon=False, fontsize=LEGEND_SIZE)

plt.tight_layout()
# Source note below the axes, outside the plot area
fig.text(0.5, 0.01,
         "Source: CDC SchoolVaxView/MMWR kindergarten vaccination coverage.",
         ha="center", va="bottom", fontsize=6, color="#555555")
plt.savefig(os.path.join(FIG_DIR, "figure1D_mmr_coverage.png"), **SAVE_KW)
plt.close()
print("  Saved: figure1D_mmr_coverage.png")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Processed data summary CSV
# ══════════════════════════════════════════════════════════════════════════════
summary_df = state_totals.reset_index()
summary_df.columns = ["state", "cumulative_2026_confirmed_cases"]
summary_df["data_source"]  = "Johns Hopkins CSSEGISandData measles_county_all_updates.csv"
summary_df["date_filter"]  = f"2026-01-01 through {DATE_MAX_STR}"
summary_df["outcome_type"] = "case_lab-confirmed"
summary_df.to_csv(os.path.join(DATA_DIR, "processed_data_summary.csv"), index=False)
print(f"\n  Saved: processed_data_summary.csv ({len(summary_df)} states)")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Normalise all four PNGs to identical pixel dimensions
# ══════════════════════════════════════════════════════════════════════════════
FIGURE_FILES = [
    "figure1A_map.png",
    "figure1B_top_states_bar.png",
    "figure1C_weekly_curves.png",
    "figure1D_mmr_coverage.png",
]
images = [Image.open(os.path.join(FIG_DIR, f)) for f in FIGURE_FILES]
max_w  = max(img.width  for img in images)
max_h  = max(img.height for img in images)

print(f"\n[Normalise] Target canvas: {max_w} × {max_h} px")
for fname, img in zip(FIGURE_FILES, images):
    if img.width == max_w and img.height == max_h:
        print(f"  {fname}: already correct size"); continue
    canvas = Image.new("RGB", (max_w, max_h), (255, 255, 255))
    canvas.paste(img.convert("RGB"),
                 ((max_w - img.width) // 2, (max_h - img.height) // 2))
    canvas.save(os.path.join(FIG_DIR, fname), dpi=(300, 300))
    print(f"  {fname}: {img.width}×{img.height} → {max_w}×{max_h}")

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Terminal summary
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "=" * 62)
print("FINAL SUMMARY")
print("=" * 62)
print(f"Shared date range    : 2026-01-01 → {DATE_MAX_STR}")
print(f"Label in figures     : {DATE_RANGE_LBL}")
print(f"Total cases (1A/1B)  : {int(state_totals.sum())} across {len(state_totals)} states")
print(f"Top 10 states (1B/1C heatmap rows):")
for i, (s, n) in enumerate(state_totals.head(10).items(), 1):
    print(f"  {i:2d}. {s:<22s}: {int(n)}")
print(f"\nHeatmap weeks        : {n_weeks}")
print(f"Map type             : {'Geographic choropleth + AK/HI insets' if MAP_AVAILABLE else 'Tile map'}")
print(f"All figures          : {max_w}×{max_h} px at 300 dpi")
print("=" * 62)

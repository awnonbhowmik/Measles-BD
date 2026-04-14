#!/usr/bin/env python3
"""
Reorganize measles_bangladesh_eda.ipynb to match paper figure order.
New order: maps first (fig01-03), 2026 outbreak (fig04-07),
           MCV1 era (fig08-10), MCV2 era (fig11-14),
           impact analysis (fig15-16), statistics (fig17-18).
"""
import json, copy

NOTEBOOK = 'measles_bangladesh_eda.ipynb'

with open(NOTEBOOK) as f:
    nb = json.load(f)

orig = nb['cells']


def code_cell(src):
    return {'cell_type': 'code', 'execution_count': None,
            'metadata': {}, 'outputs': [], 'source': src}


def md_cell(src):
    return {'cell_type': 'markdown', 'metadata': {}, 'source': src}


def get(idx):
    return copy.deepcopy(orig[idx])


def patch(idx, old, new):
    c = copy.deepcopy(orig[idx])
    c['source'] = ''.join(c['source']).replace(old, new)
    return c


# ─── Modified copies of existing cells ────────────────────────────

# Cell 2: add population lookup tables right before "Setup complete"
c2 = get(2)
pop_block = (
    "\n"
    "# ── Bangladesh national population (UN WPP 2024, absolute) ──────────────\n"
    "BD_POP = {\n"
    "    2000: 129_955_000, 2001: 131_639_000, 2002: 133_347_000,\n"
    "    2003: 135_078_000, 2004: 136_829_000, 2005: 138_598_000,\n"
    "    2006: 140_384_000, 2007: 142_186_000, 2008: 143_999_000,\n"
    "    2009: 145_820_000, 2010: 147_645_000, 2011: 149_476_000,\n"
    "    2012: 151_319_000, 2013: 153_176_000, 2014: 155_044_000,\n"
    "    2015: 156_917_000, 2016: 158_791_000, 2017: 160_657_000,\n"
    "    2018: 162_508_000, 2019: 164_336_000, 2020: 166_130_000,\n"
    "    2021: 167_886_000, 2022: 169_600_000, 2023: 171_268_000,\n"
    "    2024: 172_954_000, 2025: 174_701_000,\n"
    "}\n"
    "\n"
    "# ── BBS 2022 census — division populations ───────────────────────────────\n"
    "DIV_POP_2022 = {\n"
    "    'Dhaka'      : 44_310_000,\n"
    "    'Chattogram' : 33_580_000,\n"
    "    'Rajshahi'   : 20_340_000,\n"
    "    'Khulna'     : 17_280_000,\n"
    "    'Rangpur'    : 17_900_000,\n"
    "    'Mymensingh' : 13_360_000,\n"
    "    'Sylhet'     : 11_370_000,\n"
    "    'Barisal'    :  9_380_000,\n"
    "}\n"
    "\n"
)
c2['source'] = ''.join(c2['source']).replace(
    'print("\\nSetup complete.")',
    pop_block + 'print("\\nSetup complete.")'
)

# Cell 4: add incidence rate to analysis after era1/era2 definitions
c4 = get(4)
incidence_add = (
    "\n"
    "# ── National incidence rate (per 100,000) ───────────────────────────────\n"
    "analysis['Population']         = analysis['Year'].map(BD_POP)\n"
    "analysis['Incidence_per_100k'] = (\n"
    "    pd.to_numeric(analysis['Reported_Cases'], errors='coerce')\n"
    "    / analysis['Population'] * 100_000\n"
    ")\n"
)
c4['source'] = ''.join(c4['source']).replace(
    "print(f'MCV1 era   :",
    incidence_add + "print(f'MCV1 era   :"
)

# Heading cells — only update the figure number in the first line
def retitle(idx, old_num, new_num):
    c = get(idx)
    c['source'] = ''.join(c['source']).replace(
        f'Figure {old_num} —', f'Figure {new_num} —'
    )
    return c

c9  = retitle(9,  1, 8)
c11 = retitle(11, 2, 9)
c16 = retitle(16, 3, 11)
c18 = retitle(18, 4, 12)
c22 = retitle(22, 6, 14)
c27 = retitle(27, 7, 4)
c29 = retitle(29, 8, 5)
c31 = retitle(31, 9, 6)
c33 = retitle(33, 10, 16)

# Fig 5 heading → Fig 13, update description
c20 = get(20)
c20['source'] = (
    ''.join(c20['source'])
    .replace('Figure 5 —', 'Figure 13 —')
    .replace('Annual cases across both eras with policy milestones',
             'Annual cases and incidence rate (per 100,000) with policy milestones')
)

# Code cells — rename saved figure filenames
c10 = patch(10, 'fig01_mcv1_era_overview.png',      'fig08_mcv1_era_overview.png')
c12 = patch(12, 'fig02_mcv1_immunity_gap.png',      'fig09_mcv1_immunity_gap.png')
c17 = patch(17, 'fig03_mcv2_era_coverage.png',      'fig11_mcv2_era_coverage.png')
c19 = patch(19, 'fig04_coverage_source_gap.png',    'fig12_coverage_source_gap.png')
c23 = patch(23, 'fig06_era_comparison_boxplot.png', 'fig14_era_comparison_boxplot.png')
c28 = patch(28, 'fig07_2026_case_cascade.png',      'fig04_2026_case_cascade.png')
c30 = patch(30, 'fig08_2026_age_deaths.png',        'fig05_2026_age_deaths.png')
c32 = patch(32, 'fig09_2026_division_burden.png',   'fig06_2026_division_burden.png')
c34 = patch(34, 'fig10_vaccination_gap.png',        'fig16_vaccination_gap.png')
c37 = patch(37, 'fig13_correlation_heatmap.png',    'fig17_correlation_heatmap.png')

# Cell 36: both map filenames
c36 = get(36)
c36_src = ''.join(c36['source'])
c36_src = c36_src.replace('fig11_2026_division_cases_map.png', 'fig01_2026_division_cases_map.png')
c36_src = c36_src.replace('fig12_2026_division_cfr_map.png',   'fig02_2026_division_cfr_map.png')
c36['source'] = c36_src

# Cell 40: pairplot filename
c40 = get(40)
c40['source'] = ''.join(c40['source']).replace(
    'fig14_2026_pairplot.png', 'fig07_2026_pairplot.png'
)

# Cell 21: fig05 → fig13, add secondary incidence-rate axis
c21 = get(21)
c21_src = ''.join(c21['source'])
c21_src = c21_src.replace(
    'fig05_cases_both_eras_milestones.png',
    'fig13_cases_incidence_milestones.png'
)
incidence_axis = (
    "\n"
    "# ── Secondary axis: incidence rate per 100,000 ──────────────────────────\n"
    "ax2 = ax.twinx()\n"
    "ir_plot = analysis[analysis['Year'].between(2000, 2025)].dropna(\n"
    "    subset=['Incidence_per_100k'])\n"
    "ax2.plot(ir_plot['Year'], ir_plot['Incidence_per_100k'],\n"
    "         color='#d62728', lw=2.0, ls=':', marker='D', ms=4.5, alpha=0.85,\n"
    "         label=r'Incidence rate (per 100{,}000)')\n"
    "ax2.set_ylabel(r'Incidence Rate (per 100{,}000)',\n"
    "               color='#d62728', labelpad=6)\n"
    "ax2.tick_params(axis='y', colors='#d62728')\n"
    "ax2.yaxis.set_major_formatter(\n"
    "    mticker.FuncFormatter(lambda x, _: f'{x:.1f}'))\n"
    "h1, l1 = ax.get_legend_handles_labels()\n"
    "h2, l2 = ax2.get_legend_handles_labels()\n"
    "ax.legend(handles=h1 + h2, labels=l1 + l2,\n"
    "          framealpha=0.9, loc='upper right', fontsize=8.5)\n"
)
c21_src = c21_src.replace(
    "plt.tight_layout()\nsavefig('fig13",
    incidence_axis + "plt.tight_layout()\nsavefig('fig13"
)
c21['source'] = c21_src

# ─── NEW cells ────────────────────────────────────────────────────

# Heading for Division Maps section
new_md_maps = md_cell(
    "---\n"
    "### Division Maps --- 2026 Outbreak\n\n"
    "Choropleth maps at division level: raw cases (fig01), case fatality rate (fig02),\n"
    "and population-adjusted incidence rate per 100,000 (fig03)."
)

# NEW fig03: incidence rate choropleth
new_fig03 = code_cell(
    "# Figure 3 --- Incidence rate per 100,000 by division (2026)\n"
    "pop_df = pd.DataFrame(list(DIV_POP_2022.items()),\n"
    "                      columns=['Division', 'Population_2022'])\n"
    "gdf_ir = gdf.merge(pop_df, on='Division', how='left')\n"
    "gdf_ir['Incidence_per_100k'] = (\n"
    "    gdf_ir['Cases'] / gdf_ir['Population_2022'] * 100_000\n"
    ")\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(8, 10))\n"
    "norm_ir = mcolors.Normalize(vmin=0, vmax=gdf_ir['Incidence_per_100k'].max())\n"
    "gdf_ir.plot(column='Incidence_per_100k', cmap=CMAP, norm=norm_ir,\n"
    "            edgecolor='#444444', linewidth=0.9, ax=ax, alpha=0.92)\n"
    "\n"
    "sm3 = cm.ScalarMappable(cmap=CMAP, norm=norm_ir)\n"
    "sm3.set_array([])\n"
    "cbar3 = fig.colorbar(sm3, ax=ax, orientation='horizontal',\n"
    "                     fraction=0.04, pad=0.01, shrink=0.72, aspect=28)\n"
    "cbar3.set_label(r'Incidence Rate per 100{,}000 Population (2026)',\n"
    "                fontsize=10.5, fontweight='bold')\n"
    "cbar3.ax.tick_params(labelsize=9)\n"
    "\n"
    "for _, row in gdf_ir.iterrows():\n"
    "    cx, cy = row['centroid'].x, row['centroid'].y\n"
    "    ax.text(cx, cy + 0.06, row['Division'],\n"
    "            ha='center', va='bottom', fontsize=8.5, fontweight='bold',\n"
    "            color='#111111',\n"
    "            path_effects=[pe.withStroke(linewidth=2.5, foreground='white')])\n"
    "    ax.text(cx, cy - 0.08,\n"
    "            f\"{row['Incidence_per_100k']:.1f}\",\n"
    "            ha='center', va='top', fontsize=8, color='#222222',\n"
    "            path_effects=[pe.withStroke(linewidth=2, foreground='white')])\n"
    "\n"
    "add_scale_bar(ax, gdf_ir, bar_km=200, n_seg=4,\n"
    "              x0_frac=0.05, y0_frac=0.05)\n"
    "plt.tight_layout()\n"
    "add_compass_rose(ax, size_inch=0.82, loc='upper right')\n"
    "ax.set_axis_off()\n"
    "ax.set_title(\n"
    "    r'2026 Measles Outbreak' + '\\n'\n"
    "    + r'Incidence Rate per 100{,}000 by Division --- Bangladesh',\n"
    "    fontweight='bold', fontsize=13, pad=10)\n"
    "fig.text(0.5, 0.01,\n"
    "         f'Data reflects: {DATA_DATE}  $|$  Source: DGHS / BBS 2022 Census',\n"
    "         ha='center', fontsize=8.5, color='gray', style='italic')\n"
    "savefig('fig03_2026_division_incidence_map.png')\n"
    "\n"
    "print('\\nDivision incidence rates per 100,000:')\n"
    "for _, row in gdf_ir.sort_values('Incidence_per_100k',\n"
    "                                  ascending=False).iterrows():\n"
    "    print(f\"  {row['Division']:<12}: {row['Incidence_per_100k']:.1f}\")\n"
)

# Heading for Rt figure
new_md_rt = md_cell(
    "### Figure 10 --- Effective Reproduction Number ($R_t$) from Coverage Data\n\n"
    "When $R_t > 1$ an outbreak can sustain itself. This figure shows whether\n"
    "vaccination coverage kept $R_t$ below the epidemic threshold each year."
)

# NEW fig10: Rt model
new_fig10 = code_cell(
    "# Figure 10 --- Effective reproduction number Rt from MCV coverage\n"
    "# Rt = R0 * (1 - p_eff)\n"
    "# MCV1-only era: p_eff = p1*(1 - failure)\n"
    "# MCV2 era:      p_eff = p1 + p2*(1-p1)  (series protection, both with 3% failure)\n"
    "R0          = 15\n"
    "MCV_FAILURE = 0.03\n"
    "HIT         = 1 - 1 / R0   # herd immunity threshold ~93.3%\n"
    "\n"
    "rt_df = analysis[analysis['Year'].between(2000, 2025)].copy()\n"
    "rt_df['MCV1_WHO_%'] = pd.to_numeric(rt_df['MCV1_WHO_%'], errors='coerce')\n"
    "rt_df['MCV2_WHO_%'] = pd.to_numeric(rt_df['MCV2_WHO_%'], errors='coerce')\n"
    "\n"
    "rt_df['p1_eff']     = rt_df['MCV1_WHO_%'] / 100 * (1 - MCV_FAILURE)\n"
    "rt_df['p2_eff']     = rt_df['MCV2_WHO_%'] / 100 * (1 - MCV_FAILURE)\n"
    "rt_df['p_2dose']    = rt_df['p1_eff'] + rt_df['p2_eff'] * (1 - rt_df['p1_eff'])\n"
    "rt_df['p_eff']      = np.where(rt_df['Year'] < 2012,\n"
    "                               rt_df['p1_eff'], rt_df['p_2dose'])\n"
    "rt_df['Rt']         = R0 * (1 - rt_df['p_eff'])\n"
    "\n"
    "ymax = rt_df['Rt'].max()\n"
    "\n"
    "fig, ax = plt.subplots(figsize=(13, 6))\n"
    "era_col = [BLUE if y <= 2011 else GREEN for y in rt_df['Year']]\n"
    "ax.bar(rt_df['Year'], rt_df['Rt'],\n"
    "       color=era_col, alpha=0.75, edgecolor='white', lw=0.5, width=0.75)\n"
    "\n"
    "ax.axhline(1.0, color='red', ls='-', lw=2, zorder=5,\n"
    "           label=r'$R_t = 1$ (epidemic threshold)')\n"
    "ax.fill_between(rt_df['Year'], rt_df['Rt'], 1,\n"
    "                where=(rt_df['Rt'] > 1), interpolate=True,\n"
    "                alpha=0.22, color='red',\n"
    "                label=r'Outbreak risk zone ($R_t > 1$)')\n"
    "ax.axvline(2011.5, color='gray', ls=':', lw=1.5, alpha=0.7)\n"
    "\n"
    "# Era shading\n"
    "ax.axvspan(1999.5, 2011.5, alpha=0.05, color=BLUE)\n"
    "ax.axvspan(2011.5, 2025.5, alpha=0.05, color=GREEN)\n"
    "ax.text(2005.5, ymax * 0.96, r'MCV1-only era',\n"
    "        ha='center', va='top', fontsize=9, color=BLUE, alpha=0.85)\n"
    "ax.text(2018.0, ymax * 0.96, r'MCV1 $+$ MCV2 era',\n"
    "        ha='center', va='top', fontsize=9, color=GREEN, alpha=0.85)\n"
    "\n"
    "ax.set_xlabel(r'Year', labelpad=6)\n"
    "ax.set_ylabel(r'Effective Reproduction Number ($R_t$)')\n"
    "ax.set_title(\n"
    "    r'Estimated $R_t$ from Vaccination Coverage --- Bangladesh (2000--2025)'\n"
    "    + '\\n'\n"
    "    + r'$R_t = R_0 \\times (1 - p_{\\mathrm{eff}})$,'\n"
    "    + r'  $R_0 = 15$,  Herd immunity threshold $= 93.3\\%$'\n"
    "    + f' $|$ Data: {DATA_DATE}',\n"
    "    fontweight='bold', pad=12)\n"
    "ax.xaxis.set_major_locator(mticker.MultipleLocator(2))\n"
    "plt.xticks(rotation=45, ha='right')\n"
    "ax.set_xlim(1999.3, 2025.7)\n"
    "ax.legend(framealpha=0.9, loc='upper right', fontsize=9.5)\n"
    "ax.text(\n"
    "    0.98, 0.04,\n"
    "    r'$R_0 = 15$ (measles, South Asia)' + '\\n'\n"
    "    + r'$p_{\\mathrm{eff}}$: two-dose coverage, 3\\% primary-failure adjustment',\n"
    "    transform=ax.transAxes, ha='right', va='bottom', fontsize=8,\n"
    "    color='gray',\n"
    "    bbox=dict(boxstyle='round', fc='white', alpha=0.85, ec='none'))\n"
    "sns.despine(ax=ax)\n"
    "plt.tight_layout()\n"
    "savefig('fig10_rt_model.png')\n"
    "\n"
    "print('Years with Rt > 1 (outbreak risk):',\n"
    "      rt_df.loc[rt_df['Rt'] > 1, 'Year'].tolist())\n"
    "print(f'Peak Rt : {rt_df[\"Rt\"].max():.2f}  '\n"
    "      f'({int(rt_df.loc[rt_df[\"Rt\"].idxmax(), \"Year\"])})')\n"
    "print(f'Lowest Rt: {rt_df[\"Rt\"].min():.2f}  '\n"
    "      f'({int(rt_df.loc[rt_df[\"Rt\"].idxmin(), \"Year\"])})')\n"
)

# Heading for cases averted
new_md_averted = md_cell(
    "### Figure 15 --- Cases Averted by MCV2: Counterfactual Analysis\n\n"
    "Log-linear trend from 2000--2011 projected forward; the gap between\n"
    "projected and actual cases estimates the measles burden prevented by MCV2."
)

# NEW fig15: cases averted counterfactual
new_fig15 = code_cell(
    "# Figure 15 --- Cases averted by MCV2: counterfactual analysis\n"
    "# Method: log-linear OLS fit on 2000-2011, projected into 2012-2025\n"
    "from scipy.stats import linregress\n"
    "\n"
    "era1_cf = analysis[analysis['Year'].between(2000, 2011)].dropna(\n"
    "    subset=['Reported_Cases'])\n"
    "era2_cf = analysis[analysis['Year'].between(2012, 2025)].dropna(\n"
    "    subset=['Reported_Cases'])\n"
    "\n"
    "log_y = np.log10(era1_cf['Reported_Cases'].clip(lower=1))\n"
    "slope, intercept, r_fit, p_fit, _ = linregress(era1_cf['Year'], log_y)\n"
    "\n"
    "years_e2  = era2_cf['Year'].values\n"
    "projected = 10 ** (intercept + slope * years_e2)\n"
    "actual    = era2_cf['Reported_Cases'].values\n"
    "averted   = np.maximum(projected - actual, 0)\n"
    "\n"
    "total_averted = averted.sum()\n"
    "total_actual  = actual.sum()\n"
    "pct_reduction = total_averted / (total_averted + total_actual) * 100\n"
    "\n"
    "print(f'MCV1-era log-linear trend:  slope={slope:.4f}/yr,  '\n"
    "      f'R\\u00b2={r_fit**2:.3f},  p={p_fit:.4f}')\n"
    "print(f'Projected total 2012-2025 (no MCV2): {int(projected.sum()):,}')\n"
    "print(f'Actual total 2012-2025:              {int(total_actual):,}')\n"
    "print(f'Estimated cases averted:             {int(total_averted):,}')\n"
    "print(f'Reduction vs counterfactual:         {pct_reduction:.1f}%')\n"
    "\n"
    "fig, axes = plt.subplots(1, 2, figsize=(14, 6))\n"
    "\n"
    "# ── Left: observed vs counterfactual trend ───────────────────────────────\n"
    "axes[0].bar(era1_cf['Year'], era1_cf['Reported_Cases'],\n"
    "            color=BLUE, alpha=0.75, width=0.72,\n"
    "            edgecolor='white', label=r'MCV1-era (actual)')\n"
    "axes[0].bar(era2_cf['Year'], era2_cf['Reported_Cases'],\n"
    "            color=GREEN, alpha=0.75, width=0.72,\n"
    "            edgecolor='white', label=r'MCV2-era (actual)')\n"
    "cf_x   = np.arange(2000, 2026)\n"
    "cf_y   = 10 ** (intercept + slope * cf_x)\n"
    "axes[0].plot(cf_x, cf_y, color='red', lw=2, ls='--',\n"
    "             label=r'Counterfactual (MCV1-era trend)')\n"
    "axes[0].fill_between(years_e2, actual, projected,\n"
    "                     where=(projected > actual),\n"
    "                     alpha=0.18, color='red',\n"
    "                     label=f'Cases averted: {int(total_averted):,}')\n"
    "axes[0].axvline(2011.5, color='gray', ls=':', lw=1.5)\n"
    "axes[0].yaxis.set_major_formatter(\n"
    "    mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))\n"
    "axes[0].set_xlabel(r'Year')\n"
    "axes[0].set_ylabel(r'Reported Cases')\n"
    "axes[0].set_title(r'Observed vs.\\ Counterfactual Cases',\n"
    "                  fontweight='bold', pad=10)\n"
    "axes[0].legend(framealpha=0.9, fontsize=8.5)\n"
    "axes[0].set_xlim(1999.3, 2025.7)\n"
    "axes[0].xaxis.set_major_locator(mticker.MultipleLocator(2))\n"
    "plt.setp(axes[0].xaxis.get_majorticklabels(), rotation=45, ha='right')\n"
    "axes[0].text(\n"
    "    0.02, 0.97,\n"
    "    r'Log-linear fit: 2000--2011' + '\\n'\n"
    "    + f'$R^2 = {r_fit**2:.2f}$,  $p = {p_fit:.4f}$',\n"
    "    transform=axes[0].transAxes, ha='left', va='top', fontsize=8.5,\n"
    "    color='gray',\n"
    "    bbox=dict(boxstyle='round', fc='white', alpha=0.85, ec='none'))\n"
    "sns.despine(ax=axes[0])\n"
    "\n"
    "# ── Right: stacked annual averted vs actual ──────────────────────────────\n"
    "cf_df = (pd.DataFrame({'Year': years_e2, 'Averted': averted, 'Actual': actual})\n"
    "           .astype({'Year': int}))\n"
    "axes[1].bar(cf_df['Year'], cf_df['Averted'],\n"
    "            color=RED, alpha=0.75, width=0.72,\n"
    "            edgecolor='white', label=r'Estimated cases averted')\n"
    "axes[1].bar(cf_df['Year'], cf_df['Actual'],\n"
    "            color=GREEN, alpha=0.75, width=0.72,\n"
    "            edgecolor='white', bottom=cf_df['Averted'],\n"
    "            label=r'Actual reported cases')\n"
    "axes[1].yaxis.set_major_formatter(\n"
    "    mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))\n"
    "axes[1].set_xlabel(r'Year')\n"
    "axes[1].set_ylabel(r'Cases')\n"
    "axes[1].set_title(r'Annual Cases Averted by MCV2 (2012--2025)',\n"
    "                  fontweight='bold', pad=10)\n"
    "axes[1].legend(framealpha=0.9, fontsize=9)\n"
    "axes[1].xaxis.set_major_locator(mticker.MultipleLocator(2))\n"
    "plt.setp(axes[1].xaxis.get_majorticklabels(), rotation=45, ha='right')\n"
    "axes[1].text(\n"
    "    0.98, 0.97,\n"
    "    r'Total averted: ' + f'{int(total_averted):,}' + '\\n'\n"
    "    + r'Reduction: ' + f'{pct_reduction:.1f}' + r'\\%',\n"
    "    transform=axes[1].transAxes, ha='right', va='top',\n"
    "    fontsize=9, fontweight='bold',\n"
    "    bbox=dict(boxstyle='round', fc='#fff0e0', ec='#cc4400', alpha=0.9))\n"
    "sns.despine(ax=axes[1])\n"
    "\n"
    "fig.suptitle(\n"
    "    r'Cases Averted by MCV2 Introduction --- Bangladesh (2012--2025)'\n"
    "    + f' $|$ Data: {DATA_DATE}',\n"
    "    fontsize=12, fontweight='bold', y=1.02)\n"
    "plt.tight_layout()\n"
    "savefig('fig15_cases_averted.png')\n"
)

# Heading for regression
new_md_regression = md_cell(
    "### Figure 18 --- Log-linear Regression: Coverage vs.~Cases\n\n"
    "OLS regression of $\\log_{10}(\\mathrm{Cases})$ on MCV1 and MCV2 WHO coverage,\n"
    "quantifying the strength of the vaccine-protection relationship."
)

# NEW fig18: regression coverage vs cases
new_fig18 = code_cell(
    "# Figure 18 --- Log-linear regression: coverage vs reported cases\n"
    "from scipy.stats import linregress as _lr\n"
    "from matplotlib.lines import Line2D\n"
    "\n"
    "reg = analysis.copy()\n"
    "reg['Log_Cases'] = np.log10(\n"
    "    pd.to_numeric(reg['Reported_Cases'], errors='coerce').clip(lower=1))\n"
    "\n"
    "m1 = reg.dropna(subset=['MCV1_WHO_%', 'Log_Cases'])\n"
    "m2 = reg.dropna(subset=['MCV2_WHO_%', 'Log_Cases'])\n"
    "\n"
    "sl1, ic1, r1, p1, _ = _lr(m1['MCV1_WHO_%'], m1['Log_Cases'])\n"
    "sl2, ic2, r2, p2, _ = _lr(m2['MCV2_WHO_%'], m2['Log_Cases'])\n"
    "\n"
    "print(f'log10(Cases) ~ MCV1 WHO: slope={sl1:.4f},  R\\u00b2={r1**2:.3f},  p={p1:.4f}')\n"
    "print(f'log10(Cases) ~ MCV2 WHO: slope={sl2:.4f},  R\\u00b2={r2**2:.3f},  p={p2:.4f}')\n"
    "\n"
    "fig, axes = plt.subplots(1, 2, figsize=(14, 6))\n"
    "\n"
    "# ── MCV1 panel ───────────────────────────────────────────────────────────\n"
    "era_col_pts = [BLUE if y <= 2011 else GREEN for y in m1['Year']]\n"
    "axes[0].scatter(m1['MCV1_WHO_%'], m1['Log_Cases'],\n"
    "                c=era_col_pts, s=62, alpha=0.85,\n"
    "                edgecolors='white', lw=0.5, zorder=3)\n"
    "x1 = np.linspace(m1['MCV1_WHO_%'].min() - 2,\n"
    "                 m1['MCV1_WHO_%'].max() + 2, 120)\n"
    "axes[0].plot(x1, ic1 + sl1 * x1, color='red', lw=2, ls='--', zorder=4)\n"
    "\n"
    "for _, row in m1.iterrows():\n"
    "    if int(row['Year']) in [2000, 2005, 2012, 2019, 2024, 2025]:\n"
    "        axes[0].annotate(\n"
    "            str(int(row['Year'])),\n"
    "            xy=(row['MCV1_WHO_%'], row['Log_Cases']),\n"
    "            xytext=(3, 3), textcoords='offset points',\n"
    "            fontsize=7.5, color='#444444')\n"
    "\n"
    "axes[0].set_xlabel(r'MCV1 Coverage --- WHO Estimate (\\%)')\n"
    "axes[0].set_ylabel(r'$\\log_{10}(\\mathrm{Reported~Cases})$')\n"
    "axes[0].set_title(r'Cases vs.\\ MCV1 Coverage (2000--2025)',\n"
    "                  fontweight='bold', pad=10)\n"
    "\n"
    "legend_pts = [\n"
    "    Line2D([0],[0], marker='o', ls='', color=BLUE,  ms=8,\n"
    "           label=r'MCV1 era (2000--2011)'),\n"
    "    Line2D([0],[0], marker='o', ls='', color=GREEN, ms=8,\n"
    "           label=r'MCV2 era (2012--2025)'),\n"
    "    Line2D([0],[0], ls='--', color='red', lw=2,\n"
    "           label=(fr'OLS: $R^2={r1**2:.3f}$, '\n"
    "                  fr'slope$={sl1:.3f}$, $p={p1:.3f}$')),\n"
    "]\n"
    "axes[0].legend(handles=legend_pts, framealpha=0.9, fontsize=8)\n"
    "sns.despine(ax=axes[0])\n"
    "\n"
    "# ── MCV2 panel ───────────────────────────────────────────────────────────\n"
    "axes[1].scatter(m2['MCV2_WHO_%'], m2['Log_Cases'],\n"
    "                c=GREEN, s=62, alpha=0.85,\n"
    "                edgecolors='white', lw=0.5, zorder=3)\n"
    "x2 = np.linspace(m2['MCV2_WHO_%'].min() - 2,\n"
    "                 m2['MCV2_WHO_%'].max() + 2, 120)\n"
    "axes[1].plot(x2, ic2 + sl2 * x2, color='red', lw=2, ls='--', zorder=4)\n"
    "\n"
    "for _, row in m2.iterrows():\n"
    "    axes[1].annotate(\n"
    "        str(int(row['Year'])),\n"
    "        xy=(row['MCV2_WHO_%'], row['Log_Cases']),\n"
    "        xytext=(3, 3), textcoords='offset points',\n"
    "        fontsize=7.5, color='#444444')\n"
    "\n"
    "axes[1].set_xlabel(r'MCV2 Coverage --- WHO Estimate (\\%)')\n"
    "axes[1].set_ylabel(r'$\\log_{10}(\\mathrm{Reported~Cases})$')\n"
    "axes[1].set_title(r'Cases vs.\\ MCV2 Coverage (2012--2024)',\n"
    "                  fontweight='bold', pad=10)\n"
    "legend_pts2 = [\n"
    "    Line2D([0],[0], marker='o', ls='', color=GREEN, ms=8,\n"
    "           label=r'MCV2 era (2012--2024)'),\n"
    "    Line2D([0],[0], ls='--', color='red', lw=2,\n"
    "           label=(fr'OLS: $R^2={r2**2:.3f}$, '\n"
    "                  fr'slope$={sl2:.3f}$, $p={p2:.3f}$')),\n"
    "]\n"
    "axes[1].legend(handles=legend_pts2, framealpha=0.9, fontsize=8)\n"
    "sns.despine(ax=axes[1])\n"
    "\n"
    "fig.suptitle(\n"
    "    r'Log-linear Regression: $\\log_{10}(\\mathrm{Cases})$ vs.\\ '\n"
    "    r'MCV Coverage --- Bangladesh 2000--2025'\n"
    "    + f' $|$ Data: {DATA_DATE}',\n"
    "    fontsize=12, fontweight='bold', y=1.02)\n"
    "plt.tight_layout()\n"
    "savefig('fig18_regression_coverage_cases.png')\n"
)

# Updated Figure Index (replaces cell 41)
new_index = md_cell(
    "---\n"
    "## Figure Index\n"
    "\n"
    "| Figure | Description |\n"
    "|--------|-------------|\n"
    "| fig01 | Choropleth map --- 2026 cases by division (YlOrRd, compass, scale bar) |\n"
    "| fig02 | Choropleth map --- 2026 CFR (\\%) by division (YlOrRd, compass, scale bar) |\n"
    "| fig03 | Choropleth map --- 2026 incidence rate per 100{,}000 by division (BBS 2022 pop.) |\n"
    "| fig04 | 2026 outbreak case cascade --- absolute counts and \\% of suspected cases |\n"
    "| fig05 | 2026 outbreak --- age distribution of deaths (bar $+$ donut) |\n"
    "| fig06 | 2026 outbreak --- cases and CFR (\\%) by division (horizontal bars) |\n"
    "| fig07 | PairGrid --- 2026 district outbreak: scatter \\| KDE contour \\| KDE diagonal; "
    "axes: Cases, Deaths, CFR (\\%), $\\log_{10}$(Cases), $\\log_{10}$(Deaths$+$1) |\n"
    "| fig08 | MCV1 coverage (3 sources) and reported cases --- MCV1 era (2000--2011) |\n"
    "| fig09 | Immunity gap vs.\\ measles burden --- red bars where coverage $<$ 95\\% |\n"
    "| fig10 | Effective reproduction number $R_t$ from coverage data (2000--2025) |\n"
    "| fig11 | MCV1 and MCV2 coverage by source --- MCV2 era (2012--2025) |\n"
    "| fig12 | Coverage source discrepancy --- administrative vs.\\ official vs.\\ WHO |\n"
    "| fig13 | Measles cases and incidence rate (per 100{,}000) with policy milestones (2000--2025) |\n"
    "| fig14 | Era comparison boxplot --- MCV1-only vs.\\ MCV2 era (Mann--Whitney $U$) |\n"
    "| fig15 | Cases averted by MCV2 --- counterfactual log-linear trend analysis |\n"
    "| fig16 | Estimated vaccination gap --- annual and cumulative unprotected children |\n"
    "| fig17 | Pearson correlation heatmap --- cases vs.\\ MCV1/MCV2 coverage (2000--2026) |\n"
    "| fig18 | Log-linear regression: $\\log_{10}(\\mathrm{Cases})$ vs.\\ MCV1 and MCV2 coverage |\n"
)

# ─── Assemble new cell order ──────────────────────────────────────
# Keep originals for unchanged cells
c0  = get(0)
c1  = get(1)
c3  = get(3)
c5  = get(5)
c6  = get(6)
c7  = get(7)
c8  = get(8)
c13 = get(13)
c14 = get(14)
c15 = get(15)
c24 = get(24)
c25 = get(25)
c26 = get(26)
c38 = get(38)
c39 = get(39)

new_cells = [
    # ── Header + setup ──────────────────────────────────────────────
    c0,          # Title markdown
    c1,          # Section 0 heading
    c2,          # Setup (+ BD_POP, DIV_POP_2022)
    c3,          # Load & Preview heading
    c4,          # Data loading (+ Incidence_per_100k)
    c5,          # Dataset Overview heading
    c6,          # Inventory table

    # ── PART III — 2026 Outbreak ────────────────────────────────────
    get(25),     # Part III intro markdown
    get(26),     # Part III stats code

    # Division maps (fig01, fig02, fig03)
    new_md_maps,
    c36,         # fig01 cases map + fig02 CFR map
    new_fig03,   # fig03 incidence rate map

    # 2026 outbreak figures
    c27,         # Figure 4 heading
    c28,         # fig04 case cascade
    c29,         # Figure 5 heading
    c30,         # fig05 age deaths
    c31,         # Figure 6 heading
    c32,         # fig06 division bars
    c38,         # Summary Insights 2026

    # Pairplot (fig07)
    c39,         # Pairplot heading
    c40,         # fig07 pairplot

    # ── PART I — MCV1 era ──────────────────────────────────────────
    c7,          # Part I intro
    c8,          # Part I stats
    c9,          # Figure 8 heading
    c10,         # fig08 MCV1 coverage
    c11,         # Figure 9 heading
    c12,         # fig09 immunity gap
    new_md_rt,   # Figure 10 heading
    new_fig10,   # fig10 Rt model
    c13,         # Key Insight Part I

    # ── PART II — MCV2 era ─────────────────────────────────────────
    c14,         # Part II intro
    c15,         # Part II stats
    c16,         # Figure 11 heading
    c17,         # fig11 MCV2 coverage
    c18,         # Figure 12 heading
    c19,         # fig12 source gap
    c20,         # Figure 13 heading
    c21,         # fig13 cases + incidence rate
    c22,         # Figure 14 heading
    c23,         # fig14 era comparison
    c24,         # Key Insights Part II

    # Cases averted (fig15)
    new_md_averted,
    new_fig15,

    # Vaccination gap (fig16)
    c33,         # Figure 16 heading
    c34,         # fig16 vaccination gap

    # ── Statistical analysis ────────────────────────────────────────
    c37,         # fig17 correlation heatmap
    new_md_regression,
    new_fig18,   # fig18 regression

    # Figure Index
    new_index,
]

nb['cells'] = new_cells

with open(NOTEBOOK, 'w') as f:
    json.dump(nb, f, indent=1)

print(f"Done. New notebook has {len(new_cells)} cells.")
print("\nNew figure file mapping:")
renames = [
    ("fig11 → fig01", "fig01_2026_division_cases_map.png"),
    ("fig12 → fig02", "fig02_2026_division_cfr_map.png"),
    ("NEW    fig03",  "fig03_2026_division_incidence_map.png"),
    ("fig07 → fig04", "fig04_2026_case_cascade.png"),
    ("fig08 → fig05", "fig05_2026_age_deaths.png"),
    ("fig09 → fig06", "fig06_2026_division_burden.png"),
    ("fig14 → fig07", "fig07_2026_pairplot.png"),
    ("fig01 → fig08", "fig08_mcv1_era_overview.png"),
    ("fig02 → fig09", "fig09_mcv1_immunity_gap.png"),
    ("NEW    fig10",  "fig10_rt_model.png"),
    ("fig03 → fig11", "fig11_mcv2_era_coverage.png"),
    ("fig04 → fig12", "fig12_coverage_source_gap.png"),
    ("fig05 → fig13", "fig13_cases_incidence_milestones.png"),
    ("fig06 → fig14", "fig14_era_comparison_boxplot.png"),
    ("NEW    fig15",  "fig15_cases_averted.png"),
    ("fig10 → fig16", "fig16_vaccination_gap.png"),
    ("fig13 → fig17", "fig17_correlation_heatmap.png"),
    ("NEW    fig18",  "fig18_regression_coverage_cases.png"),
]
for label, fname in renames:
    print(f"  {label:<16}  {fname}")

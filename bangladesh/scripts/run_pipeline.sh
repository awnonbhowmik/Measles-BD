#!/usr/bin/env bash
# scripts/run_pipeline.sh
# Full daily pipeline:
#   1. Fetch latest DGHS data from BSS News → dghs_daily_updates.csv
#   2. Rebuild consolidated Excel dataset (WHO GHO API + raw data)
#   3. Re-execute the analysis notebook and regenerate all figures
#
# Designed to be run from the project root, e.g. via cron:
#   45 4 * * 1-5 /home/abhowmik/Desktop/Measles-BD/scripts/run_pipeline.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
VENV="$ROOT/venv/bin"
LOG="$ROOT/data/processed/update_log.txt"

cd "$ROOT"

echo "=========================================="
echo "Measles-BD pipeline  $(date '+%Y-%m-%dT%H:%M:%S')"
echo "=========================================="

# ── Step 1: Fetch DGHS update ───────────────────────────────────
echo ""
echo "Step 1: Fetching DGHS daily update..."
if "$VENV/python" scripts/fetch_dghs_update.py; then
    echo "  → New data appended."
else
    echo "  → No new data found (CSV already current or source unavailable)."
fi

# ── Step 2: Rebuild dataset ─────────────────────────────────────
echo ""
echo "Step 2: Rebuilding consolidated dataset..."
"$VENV/python" scripts/build_dataset.py

# ── Step 3: Execute notebook ─────────────────────────────────────
echo ""
echo "Step 3: Executing notebook and regenerating figures..."
"$VENV/jupyter" nbconvert \
    --to notebook \
    --execute \
    --ExecutePreprocessor.kernel_name=measles-bd \
    --ExecutePreprocessor.timeout=300 \
    measles_bangladesh_eda.ipynb \
    --output measles_bangladesh_eda.ipynb

echo ""
echo "=========================================="
echo "Pipeline complete  $(date '+%Y-%m-%dT%H:%M:%S')"
echo "=========================================="

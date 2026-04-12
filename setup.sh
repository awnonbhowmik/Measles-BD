#!/usr/bin/env bash
# setup.sh — one-shot setup for Measles-BD analysis
# Usage: bash setup.sh
set -e

echo "=== Measles-BD setup ==="

# 1. Check for Python 3.13+
PYTHON=$(command -v python3.13 2>/dev/null || command -v python3 2>/dev/null || true)
if [ -z "$PYTHON" ]; then
    echo "ERROR: Python 3.13 not found. Install it and try again."
    exit 1
fi
PY_VER=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJ=$("$PYTHON" -c "import sys; print(sys.version_info.major)")
PY_MIN=$("$PYTHON" -c "import sys; print(sys.version_info.minor)")
if [ "$PY_MAJ" -lt 3 ] || { [ "$PY_MAJ" -eq 3 ] && [ "$PY_MIN" -lt 13 ]; }; then
    echo "ERROR: Python 3.13+ required, found $PY_VER at $PYTHON"
    exit 1
fi
echo "Using Python $PY_VER at $PYTHON"

# 2. System LaTeX check (required for figure rendering)
if ! command -v latex &>/dev/null; then
    echo ""
    echo "WARNING: LaTeX not found. Figures will fail to render with text.usetex=True."
    echo "Install with:"
    echo "  sudo apt install texlive-latex-extra texlive-fonts-recommended cm-super"
    echo "Then re-run this script."
    echo ""
fi

# 3. Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment (venv/)..."
    "$PYTHON" -m venv venv
else
    echo "venv/ already exists, skipping creation."
fi

# 4. Install dependencies
echo "Installing dependencies from requirements.txt..."
venv/bin/pip install --upgrade pip --quiet
venv/bin/pip install -r requirements.txt --quiet
echo "Dependencies installed."

# 5. Register Jupyter kernel
echo "Registering Jupyter kernel 'measles-bd'..."
venv/bin/python -m ipykernel install --user \
    --name measles-bd \
    --display-name "Python 3.13 (measles-bd)"

# 6. Build the consolidated dataset
echo "Building consolidated dataset from WHO GHO + raw data..."
venv/bin/python scripts/build_dataset.py

echo ""
echo "=== Setup complete ==="
echo ""
echo "Launch the notebook interactively:"
echo "  venv/bin/jupyter notebook measles_bangladesh_eda.ipynb"
echo ""
echo "Or execute headlessly:"
echo "  venv/bin/jupyter nbconvert --to notebook --execute \\"
echo "    --ExecutePreprocessor.kernel_name=measles-bd \\"
echo "    measles_bangladesh_eda.ipynb --output measles_bangladesh_eda.ipynb"

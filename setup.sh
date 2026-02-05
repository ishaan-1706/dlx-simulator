#!/usr/bin/env bash
# setup.sh - POSIX quick setup for DLX simulator
VENV_DIR="sim_venv"
echo "Creating virtual environment in ${VENV_DIR}..."
python3 -m venv "${VENV_DIR}"
echo "Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
echo "Installing dependencies from requirements.txt..."
python -m pip install --upgrade pip
pip install -r requirements.txt
echo
echo "Setup complete. To run the simulator:"
echo "  source ${VENV_DIR}/bin/activate"
echo "  python main.py tests/sample_programs/simple_branch.asm"
echo
echo "Or run the sample runner: python tools/run_sample.py"

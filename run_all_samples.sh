#!/usr/bin/env bash
# Run all sample .asm programs sequentially
set -e
SAMP_DIR="tests/sample_programs"
VENV_DIR="sim_venv"

if [ -d "$VENV_DIR" ]; then
  echo "Activating virtual environment $VENV_DIR"
  # shellcheck disable=SC1091
  source "$VENV_DIR/bin/activate"
fi

if [ ! -d "$SAMP_DIR" ]; then
  echo "Sample programs directory not found: $SAMP_DIR"
  exit 1
fi

for f in "$SAMP_DIR"/*.asm; do
  [ -e "$f" ] || continue
  echo "\n===== Running: $(basename "$f") ====="
  python main.py "$f"
  echo "===== Finished: $(basename "$f") =====\n"
done

echo "All sample programs executed."

#!/usr/bin/env bash
# add_program.sh - copy a user .asm into tests/sample_programs
set -e

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/your_program.asm [optional-destination-name.asm]"
  exit 2
fi

SRC="$1"
DEST_NAME="${2:-$(basename "$SRC") }"
DEST_DIR="user_programs"

if [ ! -f "$SRC" ]; then
  echo "Source file not found: $SRC"
  exit 1
fi

mkdir -p "$DEST_DIR"
cp "$SRC" "$DEST_DIR/$DEST_NAME"
echo "Copied $SRC -> $DEST_DIR/$DEST_NAME"
echo "You can run it with: ./run_user.sh $DEST_NAME or: python $DEST_DIR/$DEST_NAME"

#!/usr/bin/env bash
# remove_program.sh - archive or remove sample programs
set -e

TARGET="$1"
USER_DIR="user_programs"

if [ -z "$TARGET" ]; then
  echo "Usage: $0 <filename.asm>|--all"
  exit 2
fi

if [ ! -d "$USER_DIR" ]; then
  echo "No user_programs directory found. Nothing to remove."
  exit 1
fi

if [ "$TARGET" = "--all" ]; then
  echo "Permanently deleting all .asm files in $USER_DIR"
  rm -f "$USER_DIR"/*.asm 2>/dev/null || true
  echo Done.
  exit 0
fi

if [ ! -f "$USER_DIR/$TARGET" ]; then
  echo "File not found: $USER_DIR/$TARGET"
  exit 1
fi

rm -f "$USER_DIR/$TARGET"
echo "Deleted $USER_DIR/$TARGET"

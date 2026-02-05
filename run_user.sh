#!/usr/bin/env bash
# run_user.sh - run a user-provided .asm from user_programs
set -e
USER_DIR="user_programs"

if [ ! -d "$USER_DIR" ]; then
  echo "No user_programs directory found. Create it and place your .asm files there, or use add_program.sh to add one."
  exit 1
fi

if [ "$#" -ge 1 ]; then
  FILE="$1"
  if [ ! -f "$USER_DIR/$FILE" ]; then
    echo "File not found: $USER_DIR/$FILE"
    exit 1
  fi
  echo "Running $USER_DIR/$FILE"
  python "$USER_DIR/$FILE"
  exit $?
fi

# Interactive: list files
echo "Available user programs:"
ls -1 "$USER_DIR"/*.asm 2>/dev/null || { echo "(none)"; exit 1; }
echo
read -p "Enter file name to run (e.g. myprog.asm): " sel
if [ -z "$sel" ]; then
  echo "No selection"; exit 1
fi
if [ ! -f "$USER_DIR/$sel" ]; then
  echo "File not found: $USER_DIR/$sel"; exit 1
fi
echo "Running $USER_DIR/$sel"
python "$USER_DIR/$sel"

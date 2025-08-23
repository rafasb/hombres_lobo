#!/usr/bin/env bash
# Script: move_md_to_docs.sh
# Purpose: create Docs/ dir (if missing) and move all .md files into it.
# Behaviour:
#  - searches repo for .md files excluding the Docs folder, .git and node_modules and dist/build folders
#  - sorts files by modification time (oldest first) and moves them into Docs/<original_path>
#  - preserves directory structure under Docs to avoid name collisions
#  - prints actions

set -euo pipefail

ROOT_DIR="$(pwd)"
DOCS_DIR="$ROOT_DIR/Docs"

echo "Repo root: $ROOT_DIR"
echo "Docs dir: $DOCS_DIR"

mkdir -p "$DOCS_DIR"

echo "Searching for .md files to move (excluding Docs, .git, node_modules, frontend/dist)..."

# Collect files, excluding common directories.
mapfile -t files < <(find . -type f -name '*.md' \
  -not -path './Docs/*' \
  -not -path './.git/*' \
  -not -path './node_modules/*' \
  -not -path './frontend/dist/*' \
  -not -path './frontend/node_modules/*' \
  -not -path './backend/__pycache__/*' \
  -not -path './backend/venv/*' )

if [ ${#files[@]} -eq 0 ]; then
  echo "No markdown files found to move. Exiting."
  exit 0
fi

# Build an array of "mtime path" to sort by mtime (oldest first)
entries=()
for f in "${files[@]}"; do
  # Use stat safely for each file
  if stat_out=$(stat -c '%Y %n' -- "$f" 2>/dev/null); then
    entries+=("$stat_out")
  fi
done

if [ ${#entries[@]} -eq 0 ]; then
  echo "No markdown files with stat info collected. Exiting."
  exit 0
fi

# Sort entries numerically by mtime (first column) and process oldest first
IFS=$'\n' sorted=($(printf '%s\n' "${entries[@]}" | sort -n))

echo "Found ${#sorted[@]} markdown files. Moving oldest first..."

for entry in "${sorted[@]}"; do
  mtime=$(awk '{print $1}' <<<"$entry")
  path=$(awk '{ $1=""; sub(/^ /, ""); print }' <<<"$entry")
  # Normalize leading ./
  relpath=${path#./}
  dest="$DOCS_DIR/$relpath"
  destdir=$(dirname "$dest")
  mkdir -p "$destdir"
  echo "Moving '$relpath' -> '${dest#./}'"
  mv -v -- "$path" "$dest"
done

echo "Move complete. Review the Docs/ directory and commit changes if OK."

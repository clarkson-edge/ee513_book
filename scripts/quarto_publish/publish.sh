#!/bin/bash
set -e

LOG_FILE="publish_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
exec 1> >(tee -a "$LOG_FILE") 2>&1
echo "Starting publish at $TIMESTAMP"

# Ensure on main and up-to-date
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo "Error: Not on main branch."
    exit 1
fi

# Push main branch first
git add .
git commit -m "Update content $(date '+%Y-%m-%d')" || true
git push origin main || {
    echo "Failed to push to main"
    exit 1
}

# Clean previous builds
rm -rf _site _book
git worktree prune

# Build and compress
quarto render
python3 scripts/quarto_publish/gs_compress_pdf.py \
    -i ./_book/Embedded-Systems-Design.pdf \
    -o ./_book/ebook.pdf \
    -s "/ebook"
mv ./_book/ebook.pdf ./_book/Embedded-Systems-Design.pdf

# Publish to gh-pages
quarto publish --no-render gh-pages || {
    rm -rf _site
    git worktree prune
    quarto publish --no-render gh-pages
}

echo "Process completed at $(date '+%Y-%m-%d_%H-%M-%S')"
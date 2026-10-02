#!/bin/sh
# Assembles docs/ from the repo sources, then builds the site into site/.
set -e
cd "$(dirname "$0")"
mkdir -p docs
cp -R authors docs/
cp INDEX.md docs/index.md
cp LICENSES.md docs/licenses.md
mkdocs "${@:-build}"

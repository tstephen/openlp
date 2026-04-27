#!/usr/bin/env bash
set -euo pipefail

export PATH="$HOME/.local/bin:$PATH"

if ! command -v hatch >/dev/null 2>&1; then
    pipx install hatch
fi

corepack enable
corepack prepare pnpm@latest --activate

cd /workspaces/openlp
hatch env create
hatch env create test
pnpm install

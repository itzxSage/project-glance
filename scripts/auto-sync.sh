#!/usr/bin/env bash
# auto-sync.sh — Project Glance data re-sync launcher.
# Regenerates data/*.json from the live sources (Kanban snapshot, OpenViking vault,
# project index). Hook this up to a scheduled job (Hermes autotask or macOS cron) so
# the Project Glance page picks up new work "as we go."
#
# Usage:
#   bash scripts/auto-sync.sh          # run from anywhere (self-locating)
#   ./scripts/auto-sync.sh

set -euo pipefail

# Self-locate: this script lives in scripts/, the repo root is one level up.
SELF="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SELF/.." && pwd)"
cd "$ROOT"

echo "[auto-sync] syncing Project Glance data in $ROOT"
python3 sync.py --demo || { echo "[auto-sync] ERROR: sync.py --demo failed" >&2; exit 1; }
echo "[auto-sync] done."

# Optional: log a fresh "last auto-sync" marker for the SPA refresh indicator.
# (Not wired by default; add cron/autotask below.)

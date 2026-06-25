#!/usr/bin/env bash
set -euo pipefail

PLUGIN_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PLUGIN_ROOT}/bin${PYTHONPATH:+:${PYTHONPATH}}"
python3 -m presecurity "$@"


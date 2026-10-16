#!/usr/bin/env bash
# ==============================================================================
# 🌍 Avani Albedo — Quick Startup & Data Orchestration Launcher
# ==============================================================================
# Usage:
#   ./run.sh                  # Start local dev server (port 8000)
#   ./run.sh --open           # Start and auto-open in browser
#   ./run.sh --stage-data     # Fetch & stage real climate telemetry into data/json_staging/
#   ./run.sh --push-bq        # Upload staged data to GCS and batch load into BigQuery ($0.00 cost)
#   ./run.sh --port 8080      # Start on custom port
# ==============================================================================

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec "${DIR}/start_local.sh" "$@"


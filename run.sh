#!/usr/bin/env bash
# Startup script for Avani Albedo
# Delegates to start_local.sh with all supplied arguments
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
exec "${DIR}/start_local.sh" "$@"


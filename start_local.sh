#!/usr/bin/env bash
# ==============================================================================
# Avani Albedo - Local Startup Script
# Prescriptive Climate Resilience & Albedo Optimization Engine
# ==============================================================================

set -e

# Resolve script directory to absolute root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${PROJECT_ROOT}"

# Default parameters
DEFAULT_PORT=8000
DEFAULT_HOST="127.0.0.1"
AUTO_OPEN=false
FORCE_INSTALL=false

# ANSI Color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
MAGENTA="\033[0;35m"
NC="\033[0m" # No Color

# Display Help
show_help() {
    echo -e "${BOLD}Avani Albedo - Local Application Launcher${NC}\n"
    echo -e "${BOLD}Usage:${NC}"
    echo -e "  ./start_local.sh [options]"
    echo -e "  or ./run.sh [options]\n"
    echo -e "${BOLD}Options:${NC}"
    echo -e "  ${CYAN}-p, --port <number>${NC}    Set server port (default: 8000, or from .env)"
    echo -e "  ${CYAN}-h, --host <ip>${NC}        Set server host (default: 127.0.0.1)"
    echo -e "  ${CYAN}-o, --open${NC}             Automatically open the web dashboard in your browser"
    echo -e "  ${CYAN}-i, --install${NC}          Force re-installation of dependencies from requirements.txt"
    echo -e "  ${CYAN}--help${NC}                 Show this help message and exit\n"
    echo -e "${BOLD}Examples:${NC}"
    echo -e "  ./start_local.sh"
    echo -e "  ./start_local.sh --open"
    echo -e "  ./start_local.sh --port 8080 --open"
    exit 0
}

# Parse command line options
while [[ $# -gt 0 ]]; do
    case "$1" in
        -p|--port)
            CUSTOM_PORT="$2"
            shift 2
            ;;
        -h|--host)
            CUSTOM_HOST="$2"
            shift 2
            ;;
        -o|--open)
            AUTO_OPEN=true
            shift
            ;;
        -i|--install)
            FORCE_INSTALL=true
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            ;;
    esac
done

echo -e "\n${BOLD}${CYAN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} 🌍 AVANI ALBEDO: Prescriptive Climate Resilience Engine${NC}"
echo -e "${BOLD}${CYAN}==============================================================================${NC}"

# 1. Environment file check (.env)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}⚠️  No .env file found. Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env successfully.${NC}"
    else
        echo -e "${YELLOW}⚠️  Warning: Neither .env nor .env.example found.${NC}"
    fi
else
    echo -e "${GREEN}✓ Environment configuration (.env) detected.${NC}"
fi

# Load default PORT and HOST from .env if present and not overridden by CLI
if [ -z "$CUSTOM_PORT" ]; then
    ENV_PORT=$(grep -E "^PORT=" .env 2>/dev/null | cut -d '=' -f2 | tr -d ' "\r' || true)
    PORT="${ENV_PORT:-$DEFAULT_PORT}"
else
    PORT="$CUSTOM_PORT"
fi

if [ -z "$CUSTOM_HOST" ]; then
    ENV_HOST=$(grep -E "^HOST=" .env 2>/dev/null | cut -d '=' -f2 | tr -d ' "\r' || true)
    HOST="${ENV_HOST:-$DEFAULT_HOST}"
else
    HOST="$CUSTOM_HOST"
fi

# Export for Python / uvicorn runtime
export PORT="$PORT"
export HOST="$HOST"

# 2. Python 3 detection
if command -v python3 &>/dev/null; then
    PY_CMD="python3"
elif command -v python &>/dev/null; then
    PY_CMD="python"
else
    echo -e "${RED}❌ Error: Python 3 is not installed or not in your PATH.${NC}"
    exit 1
fi

PY_VER=$($PY_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}✓ System Python detected: $PY_CMD (version $PY_VER)${NC}"

# 3. Virtual Environment (.venv) setup & activation
if [ ! -d ".venv" ]; then
    echo -e "${CYAN}⚙️  Creating Python virtual environment in .venv...${NC}"
    $PY_CMD -m venv .venv
    source .venv/bin/activate
    echo -e "${CYAN}📦 Installing project dependencies from requirements.txt...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Virtual environment initialized and dependencies installed.${NC}"
else
    source .venv/bin/activate
    if [ "$FORCE_INSTALL" = true ]; then
        echo -e "${CYAN}📦 Updating dependencies from requirements.txt...${NC}"
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies refreshed.${NC}"
    else
        # Quick check if essential dependencies are importable
        if ! python -c "import fastapi, uvicorn, ortools, pydantic" &>/dev/null; then
            echo -e "${YELLOW}⚠️  Missing required packages in .venv. Installing requirements.txt...${NC}"
            pip install -r requirements.txt
            echo -e "${GREEN}✓ Dependencies installed.${NC}"
        else
            echo -e "${GREEN}✓ Virtual environment (.venv) is ready and dependencies verified.${NC}"
        fi
    fi
fi

# 4. Check if the designated port is already occupied
if lsof -i :"$PORT" &>/dev/null; then
    OCCUPIER=$(lsof -ti :"$PORT" | tr '\n' ' ')
    echo -e "${YELLOW}⚠️  Port $PORT is already in use by process PID(s): $OCCUPIER${NC}"
    echo -e "${YELLOW}   Attempting to inspect or select another port...${NC}"
    read -p "Would you like to kill the existing process on port $PORT? (y/N): " -r CONFIRM
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
        kill -9 $OCCUPIER 2>/dev/null || true
        sleep 1
        echo -e "${GREEN}✓ Terminated old process on port $PORT.${NC}"
    else
        echo -e "${RED}❌ Aborted. You can specify a different port using: ./start_local.sh --port <NEW_PORT>${NC}"
        exit 1
    fi
fi

# 5. Display Startup Dashboard
URL="http://${HOST}:${PORT}"
[ "$HOST" = "0.0.0.0" ] && LOCAL_URL="http://localhost:${PORT}" || LOCAL_URL="$URL"

echo -e "\n${BOLD}${GREEN}🚀 Starting Local Development Server...${NC}"
echo -e "${CYAN}------------------------------------------------------------------------------${NC}"
echo -e "  💻 ${BOLD}Web Dashboard:${NC}    ${MAGENTA}${LOCAL_URL}${NC}"
echo -e "  📑 ${BOLD}API Swagger Docs:${NC} ${MAGENTA}${LOCAL_URL}/docs${NC}"
echo -e "  🩺 ${BOLD}Health Check API:${NC} ${MAGENTA}${LOCAL_URL}/api/status${NC}"
echo -e "  🔄 ${BOLD}Live Reload:${NC}      ${GREEN}Enabled (Auto-reloads on file change)${NC}"
echo -e "${CYAN}------------------------------------------------------------------------------${NC}"
echo -e "  🛑 ${YELLOW}Press Ctrl+C to stop the server anytime.${NC}\n"

# 6. Optional: Open in default browser
if [ "$AUTO_OPEN" = true ]; then
    (
        sleep 2
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$LOCAL_URL"
        elif command -v xdg-open &>/dev/null; then
            xdg-open "$LOCAL_URL"
        fi
    ) &
fi

# 7. Start application server
exec python run.py

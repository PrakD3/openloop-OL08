#!/usr/bin/env bash
# ============================================================
# Vigilens — Online Mode Setup Script (macOS / Linux)
# Usage: bash scripts/start-online.sh
# ============================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "  ██╗   ██╗██╗ ██████╗ ██╗██╗     ███████╗███╗   ██╗███████╗"
echo "  ██║   ██║██║██╔════╝ ██║██║     ██╔════╝████╗  ██║██╔════╝"
echo "  ██║   ██║██║██║  ███╗██║██║     █████╗  ██╔██╗ ██║███████╗"
echo "  ╚██╗ ██╔╝██║██║   ██║██║██║     ██╔══╝  ██║╚██╗██║╚════██║"
echo "   ╚████╔╝ ██║╚██████╔╝██║███████╗███████╗██║ ╚████║███████║"
echo "    ╚═══╝  ╚═╝ ╚═════╝ ╚═╝╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝"
echo -e "${NC}"
echo -e "${GREEN}  Online Mode — Cloud APIs, No Docker Needed${NC}"
echo ""

# ── Check prerequisites ────────────────────────────────────────────────────────

echo -e "${YELLOW}[1/5] Checking prerequisites...${NC}"

if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
  echo -e "${RED}ERROR: Python 3.11+ is required. Download from https://python.org${NC}"
  exit 1
fi

PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo "  ✓ Python $PY_VERSION"

if ! command -v node &>/dev/null; then
  echo -e "${RED}ERROR: Node.js 18+ is required. Download from https://nodejs.org${NC}"
  exit 1
fi
echo "  ✓ Node.js $(node --version)"

if ! command -v ffmpeg &>/dev/null; then
  echo -e "${RED}ERROR: FFmpeg is required for video processing."
  echo "  macOS:  brew install ffmpeg"
  echo -e "  Linux:  sudo apt install ffmpeg${NC}"
  exit 1
fi
echo "  ✓ FFmpeg $(ffmpeg -version 2>&1 | head -1 | awk '{print $3}')"

# ── Backend .env ───────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[2/5] Setting up backend environment...${NC}"

if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  echo "  ✓ Created backend/.env from template"
  echo ""
  echo -e "${RED}  ⚠  You must fill in at least GROQ_API_KEY in backend/.env"
  echo "     Get a free key at: https://console.groq.com${NC}"
  echo ""
  # Open .env in default editor if available
  if command -v code &>/dev/null; then
    code backend/.env
  elif command -v nano &>/dev/null; then
    echo "  Opening backend/.env in nano... (save with Ctrl+O, exit with Ctrl+X)"
    sleep 2
    nano backend/.env
  fi
else
  echo "  ✓ backend/.env already exists"
fi

# ── Frontend .env ──────────────────────────────────────────────────────────────

if [ ! -f "frontend/.env.local" ]; then
  cp frontend/.env.local.example frontend/.env.local
  # Set app mode to real
  sed -i 's/NEXT_PUBLIC_APP_MODE=.*/NEXT_PUBLIC_APP_MODE=real/' frontend/.env.local
  echo "  ✓ Created frontend/.env.local"
else
  echo "  ✓ frontend/.env.local already exists"
fi

# ── Python dependencies ────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[3/5] Installing Python dependencies (online mode — no local Whisper)...${NC}"

cd backend
if [ ! -d ".venv" ]; then
  $PYTHON -m venv .venv
  echo "  ✓ Created .venv"
fi

source .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements-online.txt
echo "  ✓ Python packages installed"
cd ..

# ── Frontend dependencies ──────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[4/5] Installing frontend dependencies...${NC}"
cd frontend
npm install --silent
echo "  ✓ npm packages installed"
cd ..

# ── Launch ─────────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[5/5] Starting Vigilens...${NC}"
echo ""
echo -e "${GREEN}  Backend  → http://localhost:8000${NC}"
echo -e "${GREEN}  Frontend → http://localhost:3000${NC}"
echo -e "${GREEN}  API Docs → http://localhost:8000/docs${NC}"
echo ""
echo "  Press Ctrl+C to stop both servers."
echo ""

# Start backend in background
cd backend
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Handle Ctrl+C — kill both
trap "echo ''; echo 'Stopping...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

wait $FRONTEND_PID

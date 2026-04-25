#!/usr/bin/env bash
# ============================================================
# Vigilens — Offline Mode (Docker)
# Usage: bash scripts/start-offline.sh
# ============================================================
set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}"
echo "  VIGILENS — Offline Mode (Docker)"
echo "  =================================="
echo -e "  Everything runs locally. No cloud API keys needed.${NC}"
echo ""

# ── Check Docker ───────────────────────────────────────────────────────────────

echo -e "${YELLOW}[1/3] Checking Docker...${NC}"

if ! command -v docker &>/dev/null; then
  echo -e "${RED}ERROR: Docker is required."
  echo "  macOS/Windows: https://www.docker.com/products/docker-desktop"
  echo -e "  Linux: https://docs.docker.com/engine/install/${NC}"
  exit 1
fi

if ! docker info &>/dev/null; then
  echo -e "${RED}ERROR: Docker daemon is not running. Please start Docker Desktop.${NC}"
  exit 1
fi
echo "  ✓ Docker $(docker --version | awk '{print $3}' | tr -d ',')"

# ── .env setup ─────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[2/3] Setting up environment...${NC}"

if [ ! -f "backend/.env" ]; then
  cp backend/.env.example backend/.env
  sed -i 's/INFERENCE_MODE=.*/INFERENCE_MODE=offline/' backend/.env
  sed -i 's/APP_MODE=.*/APP_MODE=real/' backend/.env
  echo "  ✓ Created backend/.env (offline mode)"
else
  echo "  ✓ backend/.env already exists"
fi

if [ ! -f "frontend/.env.local" ]; then
  cp frontend/.env.local.example frontend/.env.local
  sed -i 's/NEXT_PUBLIC_INFERENCE_MODE=.*/NEXT_PUBLIC_INFERENCE_MODE=offline/' frontend/.env.local
  sed -i 's/NEXT_PUBLIC_APP_MODE=.*/NEXT_PUBLIC_APP_MODE=real/' frontend/.env.local
  echo "  ✓ Created frontend/.env.local (offline mode)"
else
  echo "  ✓ frontend/.env.local already exists"
fi

# ── Docker Compose ─────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}[3/3] Building and starting Docker stack...${NC}"
echo "  First run downloads AI model layers — may take 10-20 min."
echo ""

docker compose up --build -d

echo ""
echo "  Waiting for Ollama to be ready..."

# Poll until Ollama responds
until docker exec openloop-ol08-ollama-1 ollama list &>/dev/null 2>&1; do
  sleep 3
  printf "."
done
echo ""

echo "  Pulling Ollama model (first time: ~4GB download)..."
docker exec openloop-ol08-ollama-1 ollama pull gemma3:4b

echo ""
echo -e "${GREEN}  ================================"
echo "  Vigilens is ready!"
echo "  ================================"
echo "  Frontend  → http://localhost:3000"
echo "  Backend   → http://localhost:8000"
echo "  API Docs  → http://localhost:8000/docs"
echo "  DeepSafe  → http://localhost:8001"
echo "  Ollama    → http://localhost:11434"
echo ""
echo "  Stop:  docker compose down"
echo -e "  Logs:  docker compose logs -f${NC}"
echo ""

# Open browser
if command -v open &>/dev/null; then open http://localhost:3000
elif command -v xdg-open &>/dev/null; then xdg-open http://localhost:3000
fi

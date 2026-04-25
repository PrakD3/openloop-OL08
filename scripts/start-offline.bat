@echo off
:: ============================================================
:: Vigilens — Offline Mode (Docker)
:: Usage: scripts\start-offline.bat
:: ============================================================

title Vigilens — Offline Mode (Docker)
color 0A

echo.
echo   VIGILENS — Offline Mode (Docker)
echo   ==================================
echo   Everything runs locally. No cloud API keys needed.
echo.

:: ── Check Docker ─────────────────────────────────────────────────────────────

echo [1/3] Checking Docker...

docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is required.
    echo Download from: https://www.docker.com/products/docker-desktop
    start https://www.docker.com/products/docker-desktop
    pause & exit /b 1
)
echo   OK Docker found

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Desktop is not running. Please start it and try again.
    pause & exit /b 1
)
echo   OK Docker is running

:: ── .env setup ───────────────────────────────────────────────────────────────

echo.
echo [2/3] Setting up environment...

if not exist "backend\.env" (
    copy "backend\.env.example" "backend\.env" >nul
    :: Switch to offline mode
    powershell -Command "(Get-Content 'backend\.env') -replace 'INFERENCE_MODE=.*','INFERENCE_MODE=offline' -replace 'APP_MODE=.*','APP_MODE=real' | Set-Content 'backend\.env'"
    echo   Created backend\.env (offline mode)
) else (
    echo   backend\.env already exists
)

if not exist "frontend\.env.local" (
    copy "frontend\.env.local.example" "frontend\.env.local" >nul
    powershell -Command "(Get-Content 'frontend\.env.local') -replace 'NEXT_PUBLIC_INFERENCE_MODE=.*','NEXT_PUBLIC_INFERENCE_MODE=offline' -replace 'NEXT_PUBLIC_APP_MODE=.*','NEXT_PUBLIC_APP_MODE=real' | Set-Content 'frontend\.env.local'"
    echo   Created frontend\.env.local (offline mode)
) else (
    echo   frontend\.env.local already exists
)

:: ── Docker Compose ────────────────────────────────────────────────────────────

echo.
echo [3/3] Building and starting Docker stack...
echo   This may take 10-20 minutes on first run (downloading AI model layers).
echo   Subsequent starts will be much faster.
echo.

docker compose up --build -d

if %errorlevel% neq 0 (
    echo ERROR: docker compose failed. Check the output above.
    pause & exit /b 1
)

echo.
echo   Containers started! Pulling Ollama model (first time only)...
echo   This downloads ~4GB. Grab a coffee.
echo.

:: Wait for Ollama to be ready
:wait_ollama
docker exec openloop-ol08-ollama-1 ollama list >nul 2>&1
if %errorlevel% neq 0 (
    timeout /t 3 /nobreak >nul
    goto wait_ollama
)

:: Pull the model
docker exec openloop-ol08-ollama-1 ollama pull gemma3:4b

echo.
echo   ============================
echo   Vigilens is ready!
echo   ============================
echo   Frontend  -^> http://localhost:3000
echo   Backend   -^> http://localhost:8000
echo   API Docs  -^> http://localhost:8000/docs
echo   Ollama    -^> http://localhost:11434
echo   DeepSafe  -^> http://localhost:8001
echo.
echo   To stop:  docker compose down
echo   Logs:     docker compose logs -f
echo.

start http://localhost:3000
pause

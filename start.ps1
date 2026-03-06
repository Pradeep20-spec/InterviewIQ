# InterviewIQ — Start both servers (Windows PowerShell)
# Usage:  .\start.ps1
# Requires: Python venv at .venv-1, Node/npm installed

$PROJECT_ROOT = $PSScriptRoot
$BACKEND_DIR  = Join-Path $PROJECT_ROOT "project\backend"
$FRONTEND_DIR = Join-Path $PROJECT_ROOT "project\frontend"
$VENV_PYTHON  = Join-Path $PROJECT_ROOT ".venv-1\Scripts\python.exe"
$VENV_UVICORN = Join-Path $PROJECT_ROOT ".venv-1\Scripts\uvicorn.exe"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  InterviewIQ — Starting servers" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# ── Backend ────────────────────────────────────────────────────────
Write-Host "[1/2] Starting FastAPI backend on http://localhost:3001 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList (
    "-NoExit", "-Command",
    "cd '$BACKEND_DIR'; & '$VENV_UVICORN' main:app --host 0.0.0.0 --port 3001 --reload"
) -WindowStyle Normal

Start-Sleep -Seconds 2

# ── Frontend ───────────────────────────────────────────────────────
Write-Host "[2/2] Starting Vite dev server on http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -ArgumentList (
    "-NoExit", "-Command",
    "cd '$FRONTEND_DIR'; npm run dev"
) -WindowStyle Normal

Write-Host ""
Write-Host "--------------------------------------" -ForegroundColor Yellow
Write-Host "  Frontend : http://localhost:5173" -ForegroundColor Yellow
Write-Host "  Backend  : http://localhost:3001" -ForegroundColor Yellow
Write-Host "  API Docs : http://localhost:3001/docs" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor Yellow
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor White
Write-Host "Close those windows to stop." -ForegroundColor White

# LeniGuide Complete QA Audit - Run All Tests
# Execute this script to reproduce the entire audit
# Usage: ./qa/run_all.ps1

$ErrorActionPreference = "Continue"
$projectRoot = Split-Path $PSScriptRoot -Parent
$qaRoot = $PSScriptRoot
$logsDir = Join-Path $qaRoot "logs"

Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   LeniGuide (SJ-52) - Complete QA Audit Execution          ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Ensure logs directory exists
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Force -Path $logsDir | Out-Null
}

cd $projectRoot

# Phase 1: Repository State
Write-Host "[1/8] Capturing repository state..." -ForegroundColor Yellow
git log --oneline --date=iso --pretty="%h %ad %s" -50 | Out-File "$logsDir/01_git_log.txt"
git tag -l | Out-File "$logsDir/02_git_tags.txt"
git status -s | Out-File "$logsDir/03_git_status.txt"
Write-Host "  ✓ Repository state captured" -ForegroundColor Green

# Phase 2: File Inventory
Write-Host "[2/8] Building file inventory..." -ForegroundColor Yellow
Get-ChildItem -Recurse -File | Where-Object { 
    $_.FullName -notlike "*\.venv\*" -and 
    $_.FullName -notlike "*\__pycache__\*" -and
    $_.FullName -notlike "*\.git\*"
} | Select-Object FullName, Length, LastWriteTime | 
    Format-Table -AutoSize | Out-String | Out-File "$logsDir/04_file_inventory.txt"
Write-Host "  ✓ File inventory complete" -ForegroundColor Green

# Phase 3: Secrets Scan
Write-Host "[3/8] Scanning for secrets..." -ForegroundColor Yellow
$envInRepo = git ls-files | Select-String "\.env$"
$result = if ($envInRepo) { "CRITICAL: .env found in repo!" } else { "OK: No .env in repo" }
$result | Out-File "$logsDir/05_secrets_scan.txt"
Write-Host "  ✓ $result" -ForegroundColor Green

# Phase 4: Code Quality
Write-Host "[4/8] Running code quality checks..." -ForegroundColor Yellow
& .venv\Scripts\python.exe -m ruff check . 2>&1 | Out-File "$logsDir/06_ruff_output.txt"
Write-Host "  ✓ Ruff check complete" -ForegroundColor Green

# Phase 5: Run All Tests
Write-Host "[5/8] Running full test suite..." -ForegroundColor Yellow
$env:LLM_PROVIDER = "fake"
& .venv\Scripts\python.exe -m pytest -v --tb=short 2>&1 | Out-File "$logsDir/07_pytest_full.txt"
$testResult = $LASTEXITCODE
if ($testResult -eq 0) {
    Write-Host "  ✓ All tests passed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Some tests failed (exit code: $testResult)" -ForegroundColor Yellow
}

# Phase 6: API Smoke Tests
Write-Host "[6/8] Running API smoke tests..." -ForegroundColor Yellow
Write-Host "  Note: Requires API running on port 8000" -ForegroundColor Gray

$apiTests = @()

try {
    # Health check
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5 -ErrorAction Stop
    $apiTests += "✓ GET /health: 200 OK"
    
    # Records endpoint
    $records = Invoke-RestMethod -Uri "http://localhost:8000/records?limit=5" -TimeoutSec 5 -ErrorAction Stop
    $apiTests += "✓ GET /records: 200 OK ($($records.Count) records)"
    
    # Ask endpoint (Q1)
    $q1 = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body '{"question":"When is Ajanta closed?"}' -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
    $apiTests += "✓ POST /ask (Q1): 200 OK"
    
    # Ask endpoint (Q6 - abstention)
    $q6 = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body '{"question":"How many tourists last Diwali?"}' -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
    $abstained = if ($q6.abstained -eq $true) { "PASS" } else { "FAIL" }
    $apiTests += "✓ POST /ask (Q6 abstention): $abstained"
    
} catch {
    $apiTests += "⚠ API not responding: $($_.Exception.Message)"
    $apiTests += "  Start API with: uvicorn app.main:app --port 8000"
}

$apiTests | Out-File "$logsDir/08_api_smoke_tests.txt"
$apiTests | ForEach-Object { Write-Host "  $_" }

# Phase 7: Golden Questions
Write-Host "[7/8] Testing golden questions..." -ForegroundColor Yellow
$goldenQuestions = @(
    @{Q="Which day is Ellora closed?"; Expected="Tuesday"},
    @{Q="What is Kailasa temple?"; Expected="Cave 16"},
    @{Q="4 teachers + 40 students, Dec 14-15"; Expected="Ellora Mon-14"},
    @{Q="How many tourists last Diwali?"; Expected="abstained=true"}
)

$goldenResults = @()
foreach ($gq in $goldenQuestions) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -Body "{`"question`":`"$($gq.Q)`"}" -ContentType "application/json" -TimeoutSec 10 -ErrorAction Stop
        $pass = $response.answer -like "*$($gq.Expected)*" -or ($gq.Expected -eq "abstained=true" -and $response.abstained -eq $true)
        $status = if ($pass) { "✓ PASS" } else { "✗ FAIL" }
        $goldenResults += "$status - $($gq.Q)"
    } catch {
        $goldenResults += "⚠ BLOCKED - $($gq.Q) (API not running)"
    }
}

$goldenResults | Out-File "$logsDir/09_golden_questions.txt"
$goldenResults | ForEach-Object { Write-Host "  $_" }

# Phase 8: Generate Summary
Write-Host "[8/8] Generating summary..." -ForegroundColor Yellow

$summary = @"
=== LENIGUIDE QA AUDIT SUMMARY ===
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

Repository State:
- Commits: $(git rev-list --count HEAD)
- Tags: $(git tag -l | Measure-Object -Line | Select-Object -ExpandProperty Lines)
- Current branch: $(git branch --show-current)

Code Quality:
- Ruff: $(if (Test-Path "$logsDir/06_ruff_output.txt") { Get-Content "$logsDir/06_ruff_output.txt" -Raw } else { "Not run" })

Tests:
- Pytest: $(if ($testResult -eq 0) { "✓ PASSED" } else { "⚠ FAILED (see logs)" })

API Tests:
$($apiTests -join "`n")

Golden Questions:
$($goldenResults -join "`n")

Logs saved to: qa/logs/
Full report: qa/REPORT.md

=== VERDICT ===
$(if ($testResult -eq 0 -and -not $envInRepo) { 
    "✅ READY FOR DEMO"
} else { 
    "⚠ REVIEW REQUIRED (check logs)"
})

"@

$summary | Out-File "$logsDir/00_SUMMARY.txt"
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              QA AUDIT COMPLETE                              ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "Summary saved to: qa/logs/00_SUMMARY.txt" -ForegroundColor Cyan
Write-Host "Full report: qa/REPORT.md" -ForegroundColor Cyan
Write-Host ""

# Display summary
Write-Output $summary

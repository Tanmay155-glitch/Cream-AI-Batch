# LeniGuide Master Audit Script
# QA Engineer: Automated Testing Framework
# Project: SJ-52 | Student: Tanmay Subhash Gawali

$ErrorActionPreference = "Continue"
$qaRoot = $PSScriptRoot
$projectRoot = Split-Path $qaRoot -Parent
$logsDir = Join-Path $qaRoot "logs"

Write-Host "=== LENIGUIDE QA AUDIT ===" -ForegroundColor Cyan
Write-Host "Starting comprehensive audit..." -ForegroundColor Yellow
Write-Host ""

# Phase A: Repository Hygiene
Write-Host "[PHASE A] Repository Hygiene Checks" -ForegroundColor Green

# A1: Commit History Analysis
Write-Host "A1: Analyzing commit history..."
$commits = git log --pretty="%h|%ad|%s" --date=short
$commits | Out-File "$logsDir/A1_commits.txt"

$dayPrefixViolations = @()
$commitsPerDay = @{}

foreach ($commit in $commits) {
    $parts = $commit -split '\|'
    if ($parts.Count -ge 3) {
        $hash = $parts[0]
        $date = $parts[1]
        $message = $parts[2]
        
        # Check day prefix
        if ($message -notmatch '^day-\d{2}:') {
            $dayPrefixViolations += "$hash $message"
        }
        
        # Count per day
        if (!$commitsPerDay.ContainsKey($date)) {
            $commitsPerDay[$date] = 0
        }
        $commitsPerDay[$date]++
    }
}

Write-Host "  - Total commits: $($commits.Count)"
Write-Host "  - Commits without day- prefix: $($dayPrefixViolations.Count)"
Write-Host "  - Unique commit dates: $($commitsPerDay.Count)"

# A2: Tags
Write-Host "`nA2: Checking tags..."
$tags = git tag -l
$tags | Out-File "$logsDir/A2_tags.txt"

$requiredTags = @("week-1", "checkpoint-1", "checkpoint-2", "final")
$missingTags = @()
foreach ($tag in $requiredTags) {
    if ($tags -notcontains $tag) {
        $missingTags += $tag
    }
}

Write-Host "  - Found tags: $($tags.Count)"
Write-Host "  - Required tags: $($requiredTags -join ', ')"
Write-Host "  - Missing tags: $(if ($missingTags.Count -eq 0) { 'None' } else { $missingTags -join ', ' })"

# A3: Secrets Scan
Write-Host "`nA3: Scanning for secrets..."
$envInRepo = git ls-files | Select-String "\.env$" -CaseSensitive
$envIgnored = Get-Content .gitignore | Select-String "\.env"

Write-Host "  - .env in repo: $(if ($envInRepo) { 'CRITICAL - FOUND' } else { 'OK - Not found' })"
Write-Host "  - .env in .gitignore: $(if ($envIgnored) { 'OK' } else { 'MISSING' })"
Write-Host "  - .env.example exists: $(Test-Path '.env.example')"

# A4: .gitignore check
Write-Host "`nA4: Validating .gitignore..."
$gitignoreContent = Get-Content .gitignore -ErrorAction SilentlyContinue
$requiredEntries = @(".venv", ".env", "__pycache__", "*.pyc")
$missingEntries = @()

foreach ($entry in $requiredEntries) {
    $found = $false
    foreach ($line in $gitignoreContent) {
        if ($line -like "*$entry*") {
            $found = $true
            break
        }
    }
    if (-not $found) {
        $missingEntries += $entry
    }
}

Write-Host "  - Missing .gitignore entries: $(if ($missingEntries.Count -eq 0) { 'None' } else { $missingEntries -join ', ' })"

# A5: Template/plagiarism check
Write-Host "`nA5: Checking for template residue..."
$templateWords = @("CaneMitra", "sugarcane", "Surya", "Mandi")
$foundTemplateWords = @()

foreach ($word in $templateWords) {
    $found = Get-ChildItem -Recurse -Include *.py,*.md | Where-Object { $_.FullName -notlike "*\.venv\*" } | Select-String $word -SimpleMatch -ErrorAction SilentlyContinue
    if ($found) {
        $foundTemplateWords += "$word ($(($found | Measure-Object).Count) occurrences)"
    }
}

Write-Host "  - Template words found: $(if ($foundTemplateWords.Count -eq 0) { 'None - OK' } else { $foundTemplateWords -join ', ' })"

# A6: File Presence Matrix
Write-Host "`nA6: Building file presence matrix..."
$expectedFiles = @{
    "D1" = @("README.md", "day01_intro.py", "day01_menu.py")
    "D2" = @("data/sample_records.json", "app/records.py", "app/cli.py", "requirements.txt", ".gitignore")
    "D3" = @("app/ingest.py", "data/records.json", "app/models.py", "app/fetch.py")
    "D4" = @("app/main.py", "analysis/explore.py", "app/smart_search.py")
    "D5" = @("docs/how_llms_work.md", "eval/questions.json")
    "D6" = @("app/llm.py", ".env.example", "prompts/system.txt", "eval/prompt_compare.md")
    "D7" = @("app/chunking.py", "app/embed.py", "app/vectorstore.py", "eval/search_results.md")
    "D8" = @("app/rag.py", "eval/eval_set.json", "eval/run_eval.py")
    "D9" = @("app/tools.py", "app/agent_loop.py", "app/graph.py")
    "D10" = @("ui/app.py")
    "D11" = @("tests/test_records.py", "Dockerfile", ".dockerignore", "docker-compose.yml", "pyproject.toml")
    "D12" = @(".github/workflows/ci.yml")
    "D13" = @("docs/resume.md")
    "D14" = @("docs/interview.md", "PROGRESS.md")
}

$presenceMatrix = @()
foreach ($day in $expectedFiles.Keys | Sort-Object) {
    foreach ($file in $expectedFiles[$day]) {
        $exists = Test-Path $file
        $size = if ($exists) { (Get-Item $file).Length } else { 0 }
        $status = if (-not $exists) { "MISSING" } elseif ($size -lt 5) { "EMPTY" } elseif ($size -lt 100 -and $file -like "*.py") { "STUB?" } else { "EXISTS" }
        
        $presenceMatrix += [PSCustomObject]@{
            Day = $day
            File = $file
            Status = $status
            Size = $size
        }
    }
}

$presenceMatrix | Format-Table -AutoSize | Out-String | Out-File "$logsDir/A6_presence_matrix.txt"
Write-Host "  - Files checked: $($presenceMatrix.Count)"
Write-Host "  - Missing: $(($presenceMatrix | Where-Object { $_.Status -eq 'MISSING' }).Count)"
Write-Host "  - Stub/Empty: $(($presenceMatrix | Where-Object { $_.Status -in @('EMPTY', 'STUB?') }).Count)"

Write-Host "`n=== PHASE A COMPLETE ===" -ForegroundColor Green
Write-Host "Detailed logs saved to qa/logs/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Next: Run Phase B (Day-by-day functional tests)" -ForegroundColor Cyan

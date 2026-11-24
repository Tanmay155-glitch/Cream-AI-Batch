# ============================================================================
# LeniGuide Comprehensive Testing Script
# Tests both RAG (/ask) and Agent (/agent) modes
# ============================================================================

$API_BASE = "http://localhost:8000"
$testResults = @()

function Test-Endpoint {
    param(
        [string]$TestName,
        [string]$Mode,
        [string]$Question,
        [string[]]$ExpectedKeywords,
        [bool]$ShouldAbstain = $false,
        [string[]]$ExpectedTools = @()
    )
    
    Write-Host "`n--- TEST: $TestName ---" -ForegroundColor Cyan
    Write-Host "Mode: $Mode | Question: $Question" -ForegroundColor Gray
    
    $endpoint = if ($Mode -eq "rag") { "$API_BASE/ask" } else { "$API_BASE/agent" }
    $payload = if ($Mode -eq "rag") {
        @{ question = $Question } | ConvertTo-Json
    } else {
        @{ 
            question = $Question
            thread_id = "test-session-$(Get-Date -Format 'HHmmss')"
            require_approval = $false
        } | ConvertTo-Json
    }
    
    try {
        $startTime = Get-Date
        $response = Invoke-WebRequest -Uri $endpoint -Method POST -Body $payload -ContentType "application/json" -UseBasicParsing -TimeoutSec 30
        $elapsed = ((Get-Date) - $startTime).TotalMilliseconds
        $result = $response.Content | ConvertFrom-Json
        
        # Check abstention
        $abstainMatch = if ($ShouldAbstain) {
            $result.abstained -eq $true
        } else {
            $result.abstained -eq $false
        }
        
        # Check keywords in answer
        $keywordMatches = @()
        $keywordMisses = @()
        foreach ($keyword in $ExpectedKeywords) {
            if ($result.answer -match [regex]::Escape($keyword)) {
                $keywordMatches += $keyword
            } else {
                $keywordMisses += $keyword
            }
        }
        
        # Check tools used (agent mode)
        $toolsMatch = $true
        $toolsUsed = @()
        if ($Mode -eq "agent" -and $ExpectedTools.Count -gt 0) {
            $toolsUsed = $result.tools_used
            foreach ($expectedTool in $ExpectedTools) {
                if ($toolsUsed -notcontains $expectedTool) {
                    $toolsMatch = $false
                }
            }
        }
        
        # Determine pass/fail
        $passed = $abstainMatch -and ($keywordMisses.Count -eq 0) -and $toolsMatch
        
        # Display results
        Write-Host "  Response Time: $([math]::Round($elapsed, 2)) ms" -ForegroundColor Gray
        Write-Host "  Abstained: $($result.abstained) $(if ($abstainMatch) { '[✓ MATCH]' } else { '[✗ MISMATCH]' })" -ForegroundColor $(if ($abstainMatch) { 'Green' } else { 'Red' })
        
        if ($Mode -eq "agent") {
            Write-Host "  Tools Used: $($toolsUsed -join ', ')" -ForegroundColor Gray
            if ($ExpectedTools.Count -gt 0) {
                Write-Host "    Expected: $($ExpectedTools -join ', ') $(if ($toolsMatch) { '[✓]' } else { '[✗]' })" -ForegroundColor $(if ($toolsMatch) { 'Green' } else { 'Red' })
            }
        }
        
        if ($result.sources) {
            Write-Host "  Sources: $($result.sources.Count) citations" -ForegroundColor Gray
        }
        
        Write-Host "  Keywords Found: $($keywordMatches.Count)/$($ExpectedKeywords.Count)" -ForegroundColor $(if ($keywordMisses.Count -eq 0) { 'Green' } else { 'Yellow' })
        if ($keywordMatches.Count -gt 0) {
            Write-Host "    ✓ $($keywordMatches -join ', ')" -ForegroundColor Green
        }
        if ($keywordMisses.Count -gt 0) {
            Write-Host "    ✗ Missing: $($keywordMisses -join ', ')" -ForegroundColor Red
        }
        
        Write-Host "  Answer Preview: $($result.answer.Substring(0, [Math]::Min(150, $result.answer.Length)))..." -ForegroundColor Gray
        
        Write-Host "  Result: $(if ($passed) { '✓ PASS' } else { '✗ FAIL' })" -ForegroundColor $(if ($passed) { 'Green' } else { 'Red' })
        
        $testResults += @{
            TestName = $TestName
            Mode = $Mode
            Passed = $passed
            Elapsed = $elapsed
            Abstained = $result.abstained
            KeywordMatches = $keywordMatches.Count
            KeywordTotal = $ExpectedKeywords.Count
            ToolsUsed = $toolsUsed
        }
        
        return $result
        
    } catch {
        Write-Host "  ERROR: $($_.Exception.Message)" -ForegroundColor Red
        $testResults += @{
            TestName = $TestName
            Mode = $Mode
            Passed = $false
            Error = $_.Exception.Message
        }
        return $null
    }
}

# ============================================================================
# TEST SUITE
# ============================================================================

Write-Host "`n=== SECTION 1: RAG MODE - CLOSING DAYS ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q1: Closing Days" -Mode "rag" -Question "What are the closing days for Ajanta and Ellora?" -ExpectedKeywords @("Monday", "Tuesday", "Ajanta", "Ellora")

Write-Host "`n=== SECTION 2: RAG MODE - ENTRY FEES ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q2: Entry Fees" -Mode "rag" -Question "What are the entry fees?" -ExpectedKeywords @("Rs", "40", "35")

Test-Endpoint -TestName "Q3: Children Entry" -Mode "rag" -Question "Are children allowed free entry?" -ExpectedKeywords @("15", "free", "children")

Write-Host "`n=== SECTION 3: AGENT MODE - TRIP PLANNING ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q4: Trip Planning Saturday" -Mode "agent" -Question "Plan a 1-day trip to Ajanta on Saturday" -ExpectedKeywords @("Saturday", "Ajanta", "open") -ExpectedTools @("cave_trip_planner")

Test-Endpoint -TestName "Q5: Trip Planning Tuesday (Ellora Closed)" -Mode "agent" -Question "Plan a trip to Ellora on Tuesday" -ExpectedKeywords @("Tuesday", "Ellora", "closed") -ExpectedTools @("cave_trip_planner")

Write-Host "`n=== SECTION 4: ABSTENTION TEST ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q6: Who Discovered Ajanta" -Mode "rag" -Question "Who discovered Ajanta caves?" -ExpectedKeywords @("cannot", "answer", "data") -ShouldAbstain $true

Write-Host "`n=== SECTION 5: CAVE-SPECIFIC QUERIES ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q7: Cave 2 Details" -Mode "rag" -Question "Give the Cave 2 Details" -ExpectedKeywords @("Cave", "2")

Test-Endpoint -TestName "Q8: Cave 16 Kailasa" -Mode "rag" -Question "Tell me about Ellora Cave 16 Kailasa Temple" -ExpectedKeywords @("16", "Kailasa", "Ellora")

Test-Endpoint -TestName "Q9: Ajanta Cave 1" -Mode "rag" -Question "Tell me about Ajanta Cave 1" -ExpectedKeywords @("Cave", "1", "Ajanta")

Write-Host "`n=== SECTION 6: THEMATIC QUERIES ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q10: Buddhist Caves" -Mode "rag" -Question "Show me Buddhist caves with paintings" -ExpectedKeywords @("Buddhist", "Ajanta")

Test-Endpoint -TestName "Q11: Hindu Temples" -Mode "rag" -Question "Show me Hindu temples at Ellora" -ExpectedKeywords @("Hindu", "Ellora")

Test-Endpoint -TestName "Q12: Jain Caves" -Mode "rag" -Question "Tell me about Jain caves" -ExpectedKeywords @("Jain", "Ellora")

Write-Host "`n=== SECTION 7: TIMINGS AND RULES ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q13: Opening Hours" -Mode "rag" -Question "What are the opening hours?" -ExpectedKeywords @("9", "5", "AM", "PM")

Test-Endpoint -TestName "Q14: Photography Rules" -Mode "rag" -Question "Can I take photos inside caves?" -ExpectedKeywords @("photography", "camera")

Write-Host "`n=== SECTION 8: ROUTES AND DURATION ===" -ForegroundColor Magenta
Test-Endpoint -TestName "Q15: Ajanta Route" -Mode "rag" -Question "What is the recommended route for Ajanta?" -ExpectedKeywords @("route", "Ajanta", "Cave")

Test-Endpoint -TestName "Q16: Visit Duration" -Mode "rag" -Question "How long does it take to visit all caves?" -ExpectedKeywords @("hour", "time")

Write-Host "`n=== SECTION 9: MULTI-TURN AGENT CONVERSATION ===" -ForegroundColor Magenta
$threadId = "multi-turn-test-$(Get-Date -Format 'HHmmss')"
Write-Host "Thread ID: $threadId" -ForegroundColor Gray

$payload1 = @{ question = "I want to visit caves"; thread_id = $threadId; require_approval = $false } | ConvertTo-Json
$resp1 = Invoke-WebRequest -Uri "$API_BASE/agent" -Method POST -Body $payload1 -ContentType "application/json" -UseBasicParsing
$result1 = $resp1.Content | ConvertFrom-Json
Write-Host "Turn 1: $($result1.answer.Substring(0, 100))..." -ForegroundColor Gray

$payload2 = @{ question = "Plan for Ajanta on Sunday"; thread_id = $threadId; require_approval = $false } | ConvertTo-Json
$resp2 = Invoke-WebRequest -Uri "$API_BASE/agent" -Method POST -Body $payload2 -ContentType "application/json" -UseBasicParsing
$result2 = $resp2.Content | ConvertFrom-Json
Write-Host "Turn 2: $($result2.answer.Substring(0, 100))..." -ForegroundColor Gray
Write-Host "Tools Used: $($result2.tools_used -join ', ')" -ForegroundColor Green

# ============================================================================
# SUMMARY
# ============================================================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$totalTests = $testResults.Count
$passedTests = ($testResults | Where-Object { $_.Passed -eq $true }).Count
$failedTests = $totalTests - $passedTests
$passRate = [math]::Round(($passedTests / $totalTests) * 100, 1)

Write-Host "`nTotal Tests: $totalTests" -ForegroundColor White
Write-Host "Passed: $passedTests" -ForegroundColor Green
Write-Host "Failed: $failedTests" -ForegroundColor $(if ($failedTests -eq 0) { 'Green' } else { 'Red' })
Write-Host "Pass Rate: $passRate%" -ForegroundColor $(if ($passRate -ge 90) { 'Green' } elseif ($passRate -ge 70) { 'Yellow' } else { 'Red' })

Write-Host "`nFailed Tests:" -ForegroundColor Yellow
$testResults | Where-Object { $_.Passed -eq $false } | ForEach-Object {
    Write-Host "  - $($_.TestName) [$($_.Mode)]" -ForegroundColor Red
}

Write-Host "`nAverage Response Time: $([math]::Round(($testResults | Where-Object { $_.Elapsed } | Measure-Object -Property Elapsed -Average).Average, 2)) ms" -ForegroundColor Gray

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

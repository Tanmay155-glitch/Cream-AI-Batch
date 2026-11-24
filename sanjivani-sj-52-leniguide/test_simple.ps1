# LeniGuide Test Script - RAG and Agent Mode Testing

$API_BASE = "http://localhost:8000"

function Invoke-Test {
    param(
        [string]$Name,
        [string]$Mode,
        [string]$Question
    )
    
    Write-Host ""
    Write-Host "TEST: $Name" -ForegroundColor Cyan
    Write-Host "Mode: $Mode | Question: $Question" -ForegroundColor Gray
    
    $endpoint = if ($Mode -eq "rag") { "$API_BASE/ask" } else { "$API_BASE/agent" }
    $payload = if ($Mode -eq "rag") {
        @{ question = $Question } | ConvertTo-Json
    } else {
        @{ 
            question = $Question
            thread_id = "test-$Name"
            require_approval = $false
        } | ConvertTo-Json
    }
    
    try {
        $response = Invoke-WebRequest -Uri $endpoint -Method POST -Body $payload -ContentType "application/json" -UseBasicParsing -TimeoutSec 30
        $result = $response.Content | ConvertFrom-Json
        
        Write-Host "Abstained: $($result.abstained)" -ForegroundColor $(if ($result.abstained) { 'Yellow' } else { 'Green' })
        
        if ($Mode -eq "agent" -and $result.tools_used) {
            Write-Host "Tools: $($result.tools_used -join ', ')" -ForegroundColor Magenta
        }
        
        if ($result.sources) {
            Write-Host "Sources: $($result.sources.Count)" -ForegroundColor Gray
        }
        
        $preview = $result.answer.Substring(0, [Math]::Min(200, $result.answer.Length))
        Write-Host "Answer: $preview..." -ForegroundColor White
        
        return $result
    } catch {
        Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "LENIGUIDE COMPREHENSIVE TESTING" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# RAG MODE TESTS
Write-Host ""
Write-Host "=== RAG MODE TESTS ===" -ForegroundColor Magenta

Invoke-Test -Name "Q1-Closing-Days" -Mode "rag" -Question "What are the closing days for Ajanta and Ellora?"
Invoke-Test -Name "Q2-Entry-Fees" -Mode "rag" -Question "What are the entry fees?"
Invoke-Test -Name "Q3-Children-Free" -Mode "rag" -Question "Are children allowed free entry?"
Invoke-Test -Name "Q4-Cave-2" -Mode "rag" -Question "Give the Cave 2 Details"
Invoke-Test -Name "Q5-Cave-16-Kailasa" -Mode "rag" -Question "Tell me about Ellora Cave 16 Kailasa Temple"
Invoke-Test -Name "Q6-Buddhist-Caves" -Mode "rag" -Question "Show me Buddhist caves with paintings"
Invoke-Test -Name "Q7-Opening-Hours" -Mode "rag" -Question "What are the opening hours?"
Invoke-Test -Name "Q8-Abstention" -Mode "rag" -Question "Who discovered Ajanta caves?"

# AGENT MODE TESTS  
Write-Host ""
Write-Host "=== AGENT MODE TESTS ===" -ForegroundColor Magenta

Invoke-Test -Name "A1-Trip-Saturday" -Mode "agent" -Question "Plan a 1-day trip to Ajanta on Saturday"
Invoke-Test -Name "A2-Trip-Tuesday-Ellora" -Mode "agent" -Question "Plan a trip to Ellora on Tuesday"
Invoke-Test -Name "A3-Trip-Monday-Ajanta" -Mode "agent" -Question "I want to visit Ajanta on Monday"
Invoke-Test -Name "A4-General-Trip" -Mode "agent" -Question "Help me plan a cave visit"

# THEMATIC TESTS
Write-Host ""
Write-Host "=== THEMATIC QUERIES ===" -ForegroundColor Magenta

Invoke-Test -Name "T1-Hindu-Temples" -Mode "rag" -Question "Show me Hindu temples at Ellora"
Invoke-Test -Name "T2-Jain-Caves" -Mode "rag" -Question "Tell me about Jain caves"
Invoke-Test -Name "T3-Ajanta-Route" -Mode "rag" -Question "What is the recommended route for Ajanta?"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "TESTING COMPLETE" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

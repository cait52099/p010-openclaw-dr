# Deep Research CLI - Windows PowerShell
# Only forwards arguments to run_deep_research.py

param(
    [Parameter(Position=0)]
    [string]$Topic = "",
    [string]$RunId = "",
    [ValidateSet("brief", "medium", "deep")]
    [string]$Depth = "medium",
    [int]$Budget = 10,
    [string]$Lang = "en",
    [int]$Workers = 5,
    [string]$RunsDir = "./runs",
    [switch]$NonInteractive = $false
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClawdDir = Split-Path -Parent $ScriptDir

function Show-Usage {
    Write-Host "Usage: dr.ps1 [topic] [options]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  --run-id ID           Run ID for resume"
    Write-Host "  --depth DEPTH         brief|medium|deep (default: medium)"
    Write-Host "  --budget N            Budget for sources (default: 10)"
    Write-Host "  --lang LANG           Language (default: en)"
    Write-Host "  --workers N           Number of workers (default: 5)"
    Write-Host "  --runs-dir DIR        Runs directory (default: ./runs)"
    Write-Host "  --non-interactive    Exit with code 2 if clarification needed"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  dr.ps1 'artificial intelligence trends 2024'"
    Write-Host "  dr.ps1 -Depth deep -Workers 10 'quantum computing'"
    exit 1
}

# Build arguments for Python script
$pythonArgs = @()

if ($Topic) {
    $pythonArgs += $Topic
}

if ($RunId) {
    $pythonArgs += "--run-id"
    $pythonArgs += $RunId
}

if ($Depth -ne "medium") {
    $pythonArgs += "--depth"
    $pythonArgs += $Depth
}

if ($Budget -ne 10) {
    $pythonArgs += "--budget"
    $pythonArgs += $Budget
}

if ($Lang -ne "en") {
    $pythonArgs += "--lang"
    $pythonArgs += $Lang
}

if ($Workers -ne 5) {
    $pythonArgs += "--workers"
    $pythonArgs += $Workers
}

if ($RunsDir -ne "./runs") {
    $pythonArgs += "--runs-dir"
    $pythonArgs += $RunsDir
}

if ($NonInteractive) {
    $pythonArgs += "--non-interactive"
}

# Run Python script (all logic handled there)
$env:PYTHONPATH = $ClawdDir
& python3 "$ScriptDir\run_deep_research.py" @pythonArgs

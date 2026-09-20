[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Name,

    [string]$Venue = "TBD",

    [string]$Deadline = "TBD"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$projectsRoot = Join-Path $root "projects"
$safeName = ($Name.Trim() -replace '[<>:"/\\|?*]', '-') -replace '\s+', '-'
if ([string]::IsNullOrWhiteSpace($safeName)) {
    throw "Name must contain at least one valid character."
}

$folderName = "{0}-{1}" -f (Get-Date -Format "yyyyMMdd"), $safeName
$target = Join-Path $projectsRoot $folderName
if (Test-Path -LiteralPath $target) {
    throw "Project already exists: $target"
}

$directories = @(
    "00_intake",
    "01_landscape",
    "02_idea",
    "03_baseline",
    "04_experiments/configs",
    "04_experiments/logs",
    "04_experiments/results",
    "04_experiments/plots",
    "05_paper",
    "06_review",
    "07_archive",
    "data/raw",
    "data/processed",
    "code"
)

New-Item -ItemType Directory -Path $target | Out-Null
foreach ($directory in $directories) {
    New-Item -ItemType Directory -Path (Join-Path $target $directory) -Force | Out-Null
}

function Copy-Template {
    param(
        [Parameter(Mandatory = $true)][string]$Source,
        [Parameter(Mandatory = $true)][string]$Destination
    )

    $content = Get-Content -LiteralPath $Source -Raw -Encoding UTF8
    $content = $content.Replace("{{PROJECT_NAME}}", $Name)
    $content = $content.Replace("{{VENUE}}", $Venue)
    $content = $content.Replace("{{DEADLINE}}", $Deadline)
    $content = $content.Replace("{{CREATED_DATE}}", (Get-Date -Format "yyyy-MM-dd"))
    Set-Content -LiteralPath $Destination -Value $content -Encoding UTF8
}

$templates = Join-Path $root "templates"
Copy-Template (Join-Path $templates "project_readme.md") (Join-Path $target "README.md")
Copy-Template (Join-Path $templates "research_charter.md") (Join-Path $target "RESEARCH_CHARTER.md")
Copy-Template (Join-Path $root "workflow/STATE_TEMPLATE.yaml") (Join-Path $target "STATE.yaml")
Copy-Template (Join-Path $templates "decision_log.md") (Join-Path $target "DECISIONS.md")
Copy-Template (Join-Path $templates "evidence_ledger.md") (Join-Path $target "01_landscape/EVIDENCE_LEDGER.md")
Copy-Template (Join-Path $templates "literature_matrix.csv") (Join-Path $target "01_landscape/LITERATURE_MATRIX.csv")
Copy-Template (Join-Path $templates "idea_card.md") (Join-Path $target "02_idea/IDEA_CARD.md")
Copy-Template (Join-Path $templates "baseline_repro.md") (Join-Path $target "03_baseline/BASELINE_REPRO.md")
Copy-Template (Join-Path $templates "experiment_plan.md") (Join-Path $target "04_experiments/EXPERIMENT_PLAN.md")
Copy-Template (Join-Path $templates "experiment_registry.csv") (Join-Path $target "04_experiments/EXPERIMENT_REGISTRY.csv")
Copy-Template (Join-Path $templates "claim_matrix.md") (Join-Path $target "05_paper/CLAIM_MATRIX.md")
Copy-Template (Join-Path $templates "meeting_notes.md") (Join-Path $target "00_intake/MEETING_NOTES.md")

Write-Output $target

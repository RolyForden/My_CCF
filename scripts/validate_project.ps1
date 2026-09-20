[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ProjectPath
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$resolved = (Resolve-Path -LiteralPath $ProjectPath).Path
$requiredFiles = @(
    "README.md",
    "RESEARCH_CHARTER.md",
    "STATE.yaml",
    "DECISIONS.md",
    "landscape/EVIDENCE_LEDGER.md",
    "landscape/LITERATURE_MATRIX.csv",
    "idea/IDEA_CARD.md",
    "experiments/BASELINE_REPRO.md",
    "experiments/EXPERIMENT_PLAN.md",
    "experiments/EXPERIMENT_REGISTRY.csv",
    "paper/CLAIM_MATRIX.md"
)

$errors = [System.Collections.Generic.List[string]]::new()
foreach ($relativePath in $requiredFiles) {
    $path = Join-Path $resolved $relativePath
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        $errors.Add("Missing file: $relativePath")
    }
}

$statePath = Join-Path $resolved "STATE.yaml"
if (Test-Path -LiteralPath $statePath) {
    $state = Get-Content -LiteralPath $statePath -Raw -Encoding UTF8
    $allowedStages = "INTAKE|LANDSCAPE|IDEA|BASELINE|PILOT|FULL_EXPERIMENT|WRITING|REVIEW|ARCHIVE"
    $stagePattern = '(?m)^stage:\s*"?(?:' + $allowedStages + ')"?\s*$'
    if ($state -notmatch $stagePattern) {
        $errors.Add("STATE.yaml has an invalid or missing stage.")
    }
}

$literatureHeader = "paper_id,title,year,venue,task,modality,dataset,core_mechanism,code_url,primary_source,evidence_level,fulltext_read,closest_claim,known_limit,status"
$literaturePath = Join-Path $resolved "landscape/LITERATURE_MATRIX.csv"
if ((Test-Path -LiteralPath $literaturePath) -and ((Get-Content -LiteralPath $literaturePath -TotalCount 1) -ne $literatureHeader)) {
    $errors.Add("LITERATURE_MATRIX.csv header does not match the workflow schema.")
}

$experimentHeader = "run_id,stage,hypothesis,method,baseline,dataset,split,seed,config_path,command,git_commit,gpu,start_time,end_time,status,log_path,result_path,primary_metric,metric_value,notes"
$experimentPath = Join-Path $resolved "experiments/EXPERIMENT_REGISTRY.csv"
if ((Test-Path -LiteralPath $experimentPath) -and ((Get-Content -LiteralPath $experimentPath -TotalCount 1) -ne $experimentHeader)) {
    $errors.Add("EXPERIMENT_REGISTRY.csv header does not match the workflow schema.")
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "OK: $resolved"

<#
Prepare ComfyUI model folders and print the manual model checklist.
This script does not fetch model binaries. It only creates folders and reads models_manifest.json.
#>

param(
  [string]$ComfyUIRoot = $env:COMFYUI_ROOT,
  [ValidateSet("minimal", "identity", "control", "motion", "all")]
  [string]$Tier = "minimal"
)

$ErrorActionPreference = "Stop"

function Resolve-ComfyRoot {
  param([string]$Root)
  if ([string]::IsNullOrWhiteSpace($Root)) {
    $candidates = @(
      "$HOME\ComfyUI_windows_portable\ComfyUI",
      "D:\AI\ComfyUI_windows_portable\ComfyUI",
      "C:\AI\ComfyUI_windows_portable\ComfyUI",
      "$PWD\ComfyUI_windows_portable\ComfyUI",
      "$PWD\ComfyUI"
    )
    foreach ($c in $candidates) {
      if (Test-Path $c) { return (Resolve-Path $c).Path }
    }
    throw "ComfyUIRoot was not provided. Set COMFYUI_ROOT or pass -ComfyUIRoot."
  }
  if (!(Test-Path $Root)) { throw "ComfyUIRoot not found: $Root" }
  return (Resolve-Path $Root).Path
}

$ComfyUIRoot = Resolve-ComfyRoot $ComfyUIRoot
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$manifestPath = Join-Path $scriptDir "models_manifest.json"
if (!(Test-Path $manifestPath)) { throw "Manifest not found: $manifestPath" }

$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$entries = @($manifest.entries)

$selected = switch ($Tier) {
  "minimal"  { $entries | Where-Object { $_.tier -eq "minimal" } }
  "identity" { $entries | Where-Object { $_.tier -in @("minimal", "identity") } }
  "control"  { $entries | Where-Object { $_.tier -in @("minimal", "identity", "control") } }
  "motion"   { $entries | Where-Object { $_.tier -in @("minimal", "identity", "control", "motion") } }
  "all"      { $entries | Where-Object { $_.tier -ne "optional_noncommercial" } }
}

$total = 0.0
Write-Host "ComfyUIRoot: $ComfyUIRoot" -ForegroundColor Cyan
Write-Host "Tier:        $Tier" -ForegroundColor Cyan
Write-Host ""

foreach ($e in $selected) {
  $target = Join-Path $ComfyUIRoot ($e.target_dir -replace "/", "\")
  New-Item -ItemType Directory -Force -Path $target | Out-Null
  if ($e.estimated_size_gb) { $total += [double]$e.estimated_size_gb }

  Write-Host "[$($e.tier)] $($e.id)" -ForegroundColor Green
  Write-Host "  target: $target"
  Write-Host "  source: $($e.source_page)"
  Write-Host "  size:   ~$($e.estimated_size_gb) GB"
  Write-Host "  note:   $($e.install_note)"
  Write-Host ""
}

Write-Host "Estimated additional model capacity for selected tier: ~$([math]::Round($total, 2)) GB" -ForegroundColor Yellow
Write-Host "This script created folders only. Confirm upstream licenses and put each model into the target folder manually." -ForegroundColor Yellow

<#
.SYNOPSIS
  Install/update the ComfyUI custom nodes needed for the Amemiya Rui animation pipeline.

.DESCRIPTION
  This script only installs GitHub custom node repositories and Python requirements.
  It does NOT download large model weights by default. Use download_models.ps1 or the manual checklist.

.USAGE
  powershell -ExecutionPolicy Bypass -File .\08_SCRIPTS\comfyui_setup\install_custom_nodes.ps1 -ComfyUIRoot "D:\AI\ComfyUI_windows_portable\ComfyUI"

.NOTES
  Tested target: Windows + ComfyUI portable. If your ComfyUI is venv/system-python based,
  pass -PythonExe explicitly.
#>

param(
  [string]$ComfyUIRoot = $env:COMFYUI_ROOT,
  [string]$PythonExe = "",
  [switch]$SkipRequirements,
  [switch]$IncludeExperimental
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
    throw "ComfyUIRoot was not provided and no default ComfyUI path was found. Set COMFYUI_ROOT or pass -ComfyUIRoot."
  }
  if (!(Test-Path $Root)) { throw "ComfyUIRoot not found: $Root" }
  return (Resolve-Path $Root).Path
}

function Resolve-PythonExe {
  param([string]$Root, [string]$Explicit)
  if (![string]::IsNullOrWhiteSpace($Explicit)) {
    if (!(Test-Path $Explicit)) { throw "PythonExe not found: $Explicit" }
    return (Resolve-Path $Explicit).Path
  }
  $portablePython = Join-Path (Split-Path $Root -Parent) "python_embeded\python.exe"
  $venvPython = Join-Path $Root "venv\Scripts\python.exe"
  if (Test-Path $portablePython) { return (Resolve-Path $portablePython).Path }
  if (Test-Path $venvPython) { return (Resolve-Path $venvPython).Path }
  $systemPython = (Get-Command python -ErrorAction SilentlyContinue)
  if ($systemPython) { return $systemPython.Source }
  throw "Could not find Python. Pass -PythonExe."
}

function Ensure-Git {
  if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git is not available on PATH. Install Git for Windows first."
  }
}

function Clone-Or-Pull {
  param([string]$Url, [string]$DirName, [string]$CustomNodesDir)
  $target = Join-Path $CustomNodesDir $DirName
  if (Test-Path $target) {
    Write-Host "[update] $DirName" -ForegroundColor Cyan
    git -C $target pull --ff-only
  } else {
    Write-Host "[clone]  $DirName" -ForegroundColor Green
    git clone --depth 1 $Url $target
  }
}

$ComfyUIRoot = Resolve-ComfyRoot $ComfyUIRoot
$PythonExe = Resolve-PythonExe $ComfyUIRoot $PythonExe
$CustomNodesDir = Join-Path $ComfyUIRoot "custom_nodes"
if (!(Test-Path $CustomNodesDir)) { New-Item -ItemType Directory -Force -Path $CustomNodesDir | Out-Null }

Ensure-Git

Write-Host "ComfyUIRoot: $ComfyUIRoot"
Write-Host "PythonExe:    $PythonExe"
Write-Host "custom_nodes: $CustomNodesDir"

$nodes = @(
  @{ name = "comfyui-manager"; url = "https://github.com/Comfy-Org/ComfyUI-Manager.git"; tier = "core" },
  @{ name = "ComfyUI-VideoHelperSuite"; url = "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git"; tier = "core" },
  @{ name = "ComfyUI-KJNodes"; url = "https://github.com/kijai/ComfyUI-KJNodes.git"; tier = "core" },
  @{ name = "ComfyUI-LivePortraitKJ"; url = "https://github.com/kijai/ComfyUI-LivePortraitKJ.git"; tier = "core" },
  @{ name = "comfyui_controlnet_aux"; url = "https://github.com/Fannovel16/comfyui_controlnet_aux.git"; tier = "control" },
  @{ name = "ComfyUI_IPAdapter_plus"; url = "https://github.com/cubiq/ComfyUI_IPAdapter_plus.git"; tier = "identity" },
  @{ name = "ComfyUI-AnimateDiff-Evolved"; url = "https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved.git"; tier = "motion" },
  @{ name = "ComfyUI-Advanced-ControlNet"; url = "https://github.com/Kosinkadink/ComfyUI-Advanced-ControlNet.git"; tier = "motion" },
  @{ name = "ComfyUI-Impact-Pack"; url = "https://github.com/ltdrdata/ComfyUI-Impact-Pack.git"; tier = "utility" },
  @{ name = "ComfyUI-Custom-Scripts"; url = "https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git"; tier = "utility" }
)

if (!$IncludeExperimental) {
  $nodes = $nodes | Where-Object { $_.tier -ne "experimental" }
}

foreach ($n in $nodes) {
  Clone-Or-Pull -Url $n.url -DirName $n.name -CustomNodesDir $CustomNodesDir
}

# Create model directories used by this pipeline.
$modelDirs = @(
  "liveportrait",
  "animatediff_models",
  "animatediff_motion_lora",
  "controlnet",
  "ipadapter",
  "clip_vision",
  "insightface\buffalo_l"
)
foreach ($d in $modelDirs) {
  $path = Join-Path (Join-Path $ComfyUIRoot "models") $d
  New-Item -ItemType Directory -Force -Path $path | Out-Null
}

if (!$SkipRequirements) {
  foreach ($n in $nodes) {
    $nodeDir = Join-Path $CustomNodesDir $n.name
    $req = Join-Path $nodeDir "requirements.txt"
    if (Test-Path $req) {
      Write-Host "[pip] $($n.name) requirements.txt" -ForegroundColor Yellow
      & $PythonExe -s -m pip install -r $req
    }
  }
}

Write-Host ""
Write-Host "Done. Restart ComfyUI, then open Manager and install missing nodes if any are flagged." -ForegroundColor Green
Write-Host "Next: run download_models.ps1 -Tier minimal, then do manual node placement in ComfyUI." -ForegroundColor Green

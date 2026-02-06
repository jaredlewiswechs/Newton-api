# setup_newton_suite.ps1
# PowerShell equivalent of the bash setup script

param(
    [Parameter(Mandatory=$true)]
    [string]$TargetPath
)

$ErrorActionPreference = "Stop"

# Get the source root (parent of scripts directory)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceRoot = Split-Path -Parent $ScriptDir

$Projects = @(
    "realTinyTalk",
    "adan",
    "adan_portable",
    "newton_agent",
    "statsy"
)

# Create target directory
if (!(Test-Path $TargetPath)) {
    New-Item -ItemType Directory -Path $TargetPath | Out-Null
}

# Check if target is already a git repo
if (Test-Path (Join-Path $TargetPath ".git")) {
    Write-Error "Target already looks like a git repo: $TargetPath"
    exit 1
}

# Copy each project
foreach ($project in $Projects) {
    $sourcePath = Join-Path $SourceRoot $project
    $targetProjectPath = Join-Path $TargetPath $project

    if (!(Test-Path $sourcePath)) {
        Write-Error "Missing project directory: $sourcePath"
        exit 1
    }

    Write-Host "Copying $project..."
    # Use robocopy for better performance and reliability
    $robocopyArgs = @(
        $sourcePath,
        $targetProjectPath,
        "/MIR",  # Mirror directory tree
        "/NFL",  # No file list
        "/NDL",  # No directory list
        "/NJH",  # No job header
        "/NJS"   # No job summary
    )
    & robocopy @robocopyArgs | Out-Null
}

# Copy README
$readmeSource = Join-Path $SourceRoot "docs\newton_suite\README.md"
$readmeTarget = Join-Path $TargetPath "README.md"
if (Test-Path $readmeSource) {
    Copy-Item $readmeSource $readmeTarget
} else {
    Write-Warning "README.md not found at: $readmeSource"
}

# Initialize git repo
Push-Location $TargetPath
try {
    git init
    git add .
    git status --short
} finally {
    Pop-Location
}

Write-Host "Newton suite setup complete at: $TargetPath"
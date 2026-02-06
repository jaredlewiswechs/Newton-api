# PowerShell runner for Windows
$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $root\..\
if (-not (Test-Path .venv)) {
    python -m venv .venv
}
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python realTinyTalk/web/server.py

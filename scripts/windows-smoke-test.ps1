# Windows real-user clean-venv smoke test. User runs locally after extracting ZIP.
# Creates a disposable Python venv in TEMP, installs only declared astronomy requirements.
# Does not read birth profiles or contact any service except standard pip package download.
[CmdletBinding()]
param(
  [switch]$SkipInstall,
  [switch]$CheckCodexInstalled
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root 'SKILL.md'))) { throw 'Skill root not found' }
$base=Join-Path $env:TEMP ('symbolic-reflection-qa-'+[guid]::NewGuid().ToString('N').Substring(0,12))
New-Item -Path $base -ItemType Directory -Force | Out-Null
Write-Host ('Verification workspace: '+$base)
$python='python'
if (Get-Command py -ErrorAction SilentlyContinue) { $python='py' }
& $python -m venv (Join-Path $base 'venv')
if ($LASTEXITCODE -ne 0) { throw 'Python venv creation failed: install Python 3.10+ and ensure venv is available' }
$venvPython=Join-Path $base 'venv\Scripts\python.exe'
if (-not $SkipInstall) {
  & $venvPython -m pip install --only-binary=:all: -r (Join-Path $root 'requirements-astronomy.txt')
  if ($LASTEXITCODE -ne 0) { throw 'Optional astronomy dependency install failed; see pip log and check network/proxy' }
}
& $venvPython (Join-Path $root 'scripts\validate_skill.py')
if ($LASTEXITCODE -ne 0) { throw 'Skill local structural validation failed' }
& $venvPython (Join-Path $root 'scripts\build_demo.py') --check
if ($LASTEXITCODE -ne 0) { throw 'Offline browser catalog parity failed' }
$report=Join-Path $base 'installation-report.json'
$flags=@('--require-astronomy','--report',$report)
if ($CheckCodexInstalled) { $flags+= '--installed' }
& $venvPython (Join-Path $root 'scripts\install_diagnostics.py') @flags
if ($LASTEXITCODE -ne 0) { throw ('Installation diagnostics failed. Report: '+$report) }
Push-Location $root
try {
  & $venvPython -m unittest discover -s tests -v
  if ($LASTEXITCODE -ne 0) { throw 'Unit test failure' }
} finally { Pop-Location }
Write-Host 'PASS: User-side isolated Python environment completed. Check the JSON report for details.'
Write-Host ('Local report: '+$report)
Write-Host 'This verifies the current Windows runtime, NOT every possible user configuration.'

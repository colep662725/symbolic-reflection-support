# Interactive, opt-in official Horizons + Swiss audit on user's Windows machine.
# No personal birth data are requested or transmitted; only fixed public epochs.
[CmdletBinding()]
param(
  [string]$Contact = '',
  [string]$EphemerisRoot = '',
  [string]$OutputDir = ''
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root 'SKILL.md'))) { throw 'Skill directory not found' }
if (-not $EphemerisRoot) { $EphemerisRoot = Join-Path $env:USERPROFILE '.swisseph\ephe' }
if (-not $OutputDir) { $OutputDir = Join-Path $root '.horizons-audit' }
if (-not $Contact) { $Contact = Read-Host 'NASA/JPL contact email or HTTPS project URL' }
if (-not $Contact) { throw 'Contact required for NASA/JPL API fair use' }

$py = Get-Command py -ErrorAction SilentlyContinue
if (-not $py) { throw 'Python launcher py is missing. Run Python 3.13 installation first.' }
Write-Host '1/3 Verify local Swiss body-center ephemeris (9999)'
& py -3 (Join-Path $root 'scripts\fetch_horizons.py') --check-center-ephe --swiss-ephe-path $EphemerisRoot
if ($LASTEXITCODE -ne 0) { throw 'Swiss 9999 local calculation failed. Check the separate licensed ephemeris data file.' }

Write-Host '2/3 Fetch official NASA/JPL Horizons data and compare all three matched targets'
New-Item -Path $OutputDir -ItemType Directory -Force | Out-Null
& py -3 (Join-Path $root 'scripts\fetch_horizons.py') --fetch --strict `
    --contact $Contact `
    --targets Moon PlutoBarycenter PlutoCenter `
    --swiss-engine swieph --compare-swiss-center `
    --swiss-ephe-path $EphemerisRoot `
    --output-dir $OutputDir
if ($LASTEXITCODE -ne 0) {
    Write-Warning 'OFFICIAL AUDIT INCOMPLETE. Inspect fetch_failure.json and manifest.json in the directory below.'
    Write-Host $OutputDir
    throw 'NASA/JPL download or numerical verification failed. Do not claim official PASS.'
}

Write-Host '3/3 Recompare the captured raw response (archive itself is not re-authentication)'
& py -3 (Join-Path $root 'scripts\fetch_horizons.py') --from-archive $OutputDir --strict `
    --targets Moon PlutoBarycenter PlutoCenter `
    --swiss-engine swieph --compare-swiss-center `
    --swiss-ephe-path $EphemerisRoot
if ($LASTEXITCODE -ne 0) { throw 'Archive consistency failed. Preserve files for investigation.' }
Write-Host 'PASS: Official in-session NASA download and matched-target comparison completed on this machine.' -ForegroundColor Green
Write-Host ('Audit files: ' + $OutputDir)
Write-Host 'Do not upload personal birth information or authentication tokens.'

# Publish openinjectability to PyPI (alpha 0.1.0 workflow).
# Does not invent tokens. Requires credentials already configured.
#
# Preferred:
#   $env:TWINE_USERNAME = '__token__'
#   $env:TWINE_PASSWORD = 'pypi-...'   # never commit
#   .\scripts\publish_pypi.ps1
#
# Or use %USERPROFILE%\.pypirc (username = __token__, password = pypi-...).
#
# Optional: -TestPyPI to upload to TestPyPI instead of production.

[CmdletBinding()]
param(
    [switch]$TestPyPI,
    [switch]$SkipBuild,
    [switch]$SkipCheck
)

$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

function Test-CredsPresent {
    if ($env:TWINE_USERNAME -and $env:TWINE_PASSWORD) { return $true }
    if ($env:UV_PUBLISH_TOKEN) { return $true }
    if ($env:UV_PUBLISH_USERNAME -and $env:UV_PUBLISH_PASSWORD) { return $true }
    if (Test-Path (Join-Path $env:USERPROFILE '.pypirc')) { return $true }
    return $false
}

if (-not (Test-CredsPresent)) {
    Write-Error @"
No PyPI credentials detected.
Set TWINE_USERNAME=__token__ and TWINE_PASSWORD=<API token>, or create ~/.pypirc.
See docs/pypi-publish-blocker.md. Secrets were not printed.
"@
}

if (-not $SkipBuild) {
    Write-Host 'Building sdist + wheel...'
    python -m build
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

$dist = Get-ChildItem -Path (Join-Path $Root 'dist') -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -like 'openinjectability-*.tar.gz' -or $_.Name -like 'openinjectability-*-py3-none-any.whl' }
if (-not $dist) {
    Write-Error 'No dist/openinjectability-* artifacts found. Run python -m build first.'
}

Write-Host 'Dist artifacts:'
$dist | ForEach-Object { Write-Host ('  ' + $_.FullName) }

if (-not $SkipCheck) {
    Write-Host 'Running twine check...'
    python -m twine check dist/*
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Write-Host 'Reminder: 0.1.0 is ALPHA; experimental_validation_pending; literature comparison is not independent validation.'

if ($TestPyPI) {
    Write-Host 'Uploading to TestPyPI...'
    python -m twine upload --repository testpypi --non-interactive dist/*
} else {
    Write-Host 'Uploading to PyPI...'
    python -m twine upload --non-interactive dist/*
}

exit $LASTEXITCODE

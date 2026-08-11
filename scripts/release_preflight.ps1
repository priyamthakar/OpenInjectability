# Local, credential-free preflight for an OpenInjectability release.
# Publishing is performed only by .github/workflows/publish.yml via PyPI OIDC.

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $RepoRoot

git diff --quiet
if ($LASTEXITCODE -ne 0) { Write-Error 'Release preflight requires no unstaged tracked changes.' }
git diff --cached --quiet
if ($LASTEXITCODE -ne 0) { Write-Error 'Release preflight requires no staged changes.' }

$Version = python -c "ns = {}; exec(open('src/openinjectability/_version.py', encoding='utf-8').read(), ns); print(ns['__version__'])"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Running release preflight for openinjectability $Version"

python -m pytest --cov=openinjectability --cov-branch --cov-fail-under=87
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m ruff check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m ruff format --check .
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m mypy --strict src
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python -m twine check dist/*
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

python scripts/verify_distribution.py dist
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host 'Preflight passed. Publish by creating the matching GitHub release tag.'

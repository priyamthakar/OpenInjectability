# PyPI publish blocker — openinjectability 0.1.0

**Date prepared:** 2026-08-02  
**Package:** `openinjectability` **0.1.0** (alpha)  
**Published:** **no**

## Why upload did not run

No PyPI credentials were available in this environment:

| Source | Status |
|--------|--------|
| `TWINE_USERNAME` / `TWINE_PASSWORD` | not set |
| `UV_PUBLISH_TOKEN` / `UV_PUBLISH_USERNAME` / `UV_PUBLISH_PASSWORD` | not set |
| `%USERPROFILE%\.pypirc` | missing |
| Secrets printed | never (check was presence-only) |

No tokens were invented. No force-push was performed.

## What was prepared

1. **README Status** — alpha + `experimental_validation_pending` + literature comparison is **not** independent validation.
2. **CHANGELOG.md** — accurate `0.1.0` release notes (scientific boundary includes experimental validation pending).
3. **Build** — `python -m build` succeeded.
4. **Dist artifacts** (rebuild before upload if source changed after this note):

   - `dist/openinjectability-0.1.0.tar.gz`
   - `dist/openinjectability-0.1.0-py3-none-any.whl`

5. **Helper script** — [`scripts/publish_pypi.ps1`](../scripts/publish_pypi.ps1)

## Alpha / validation language (do not dilute)

- PyPI classifier: `Development Status :: 3 - Alpha`
- Status vocabulary: `internal_validation` with `experimental_validation_pending`
- Literature / digitized comparisons under `validation/experimental/` are **not** independent experimental validation
- Do not market 0.1.0 as experimentally validated

## Exact commands for the user

### Option A — API token via environment (recommended)

Create a token at https://pypi.org/manage/account/token/ (scope: entire account or project `openinjectability`).

```powershell
cd E:\OpenInjectability

# Optional clean rebuild
python -m pip install -U build twine
python -m build

# Presence-only: do not echo secrets
if (-not $env:TWINE_PASSWORD) { throw 'Set TWINE_PASSWORD to your PyPI API token' }

$env:TWINE_USERNAME = '__token__'
# $env:TWINE_PASSWORD = 'pypi-...'   # set in your shell; never commit

python -m twine check dist/*
python -m twine upload --non-interactive dist/*
```

Or use the helper:

```powershell
$env:TWINE_USERNAME = '__token__'
$env:TWINE_PASSWORD = 'pypi-...'   # your token
.\scripts\publish_pypi.ps1
```

### Option B — `~/.pypirc` (do not commit this file)

```ini
[pypi]
username = __token__
password = pypi-...
```

Then:

```powershell
cd E:\OpenInjectability
python -m build
python -m twine check dist/*
python -m twine upload --non-interactive dist/*
```

### Option C — TestPyPI first

```powershell
python -m twine upload --repository testpypi --non-interactive dist/*
# Install check:
# pip install -i https://test.pypi.org/simple/ openinjectability==0.1.0
```

### Option D — `uv` publish (if you use uv)

```powershell
$env:UV_PUBLISH_TOKEN = 'pypi-...'
uv publish
```

## Post-upload verification

```powershell
pip index versions openinjectability
# or
pip install openinjectability==0.1.0
openinjectability version
openinjectability validation-status --json
```

Confirm `validation-status` still reports experimental validation pending after install.

## If the name is taken or upload fails

- Name conflict: choose another project name or claim ownership on PyPI.
- File already exists: bump version (do not re-upload the same 0.1.0 files).
- 403: token scope or username must be `__token__` for API tokens.

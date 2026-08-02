# PyPI publish status — openinjectability 0.1.0

**Published:** **yes** (2026-08-02)  
**URL:** https://pypi.org/project/openinjectability/0.1.0/

## Verified

```powershell
python -m pip install openinjectability==0.1.0
openinjectability --version   # 0.1.0
```

## How it was published

- Account-scoped API token in user `~\.pypirc` (not in git)
- `python -m build` + `python -m twine upload dist/*`

## Later releases

```powershell
cd E:\OpenInjectability
# bump version in pyproject.toml / __init__.py / CHANGELOG first
python -m build
python -m twine upload dist/*
```

Or: `.\scripts\publish_pypi.ps1` (uses `~\.pypirc` or `TWINE_*` env).

## Security

If the API token was ever pasted into chat or a log, **revoke it** on PyPI and
create a new entire-account token; update `~\.pypirc` only (never commit).

## Scientific boundary

Alpha on PyPI is **not** independently experimentally validated. Package status
remains `experimental_validation_pending`.

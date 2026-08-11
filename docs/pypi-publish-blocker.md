# PyPI release status and Trusted Publishing setup

**Current public release:** 0.1.0 (published 2026-08-02)

**Prepared repository release:** 0.1.1 (not yet published)

**URL:** https://pypi.org/project/openinjectability/

## Current public install

```powershell
python -m pip install openinjectability==0.1.0
openinjectability --version   # 0.1.0
```

## 0.1.1 one-time setup

1. In PyPI project settings, add a pending Trusted Publisher for:
   - owner: `priyamthakar`
   - repository: `OpenInjectability`
   - workflow: `publish.yml`
   - environment: `pypi`
2. In GitHub repository settings, create environment `pypi` and require manual approval.
3. Revoke the former long-lived PyPI token. The 0.1.1 workflow does not use
   `.pypirc`, `TWINE_PASSWORD`, or another publication secret.

## Local preflight

```powershell
cd E:\OpenInjectability
.\scripts\release_preflight.ps1
```

The preflight is credential-free and never uploads. It requires a clean working tree and
runs the suite, coverage gate, repository-wide Ruff checks, strict mypy, build, and
`twine check`.

## Publish 0.1.1

After merging a clean, fully green commit, create and publish GitHub release `v0.1.1`.
`.github/workflows/publish.yml` verifies that the tag matches the package version, builds
and checks the distributions, then requests a short-lived PyPI OIDC credential through
the protected `pypi` environment.

Do not restore token publication as a fallback. If Trusted Publishing fails, diagnose
the owner/repository/workflow/environment identity and rerun the GitHub release workflow.

## Scientific boundary

Neither 0.1.0 nor 0.1.1 is independently experimentally validated. Package status
remains `experimental_validation_pending`.

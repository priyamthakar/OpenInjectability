# Experimental comparison report

- Generated (UTC): `2026-08-02T04:01:37+00:00`
- Package version: `0.1.0`
- Input panel: `validation\experimental\panel_allmendinger2014_glycerol_digitized.json`
- Input SHA-256: `f67c12f6ce53ec41233cb215f429f2f069b72746715a27c7fa910e15319e5b7a`
- Report status: **experimental_comparison**
- Comparable rows (n): `12`
- Rejected rows: `0`
- Median absolute relative error: `0.1345819629581363`
- Criterion (median abs relative error ≤): `0.2`
- Pass/fail vs criterion: `pass`

## Important

- This report status is **never** `independently_validated`.
- Package `validation_status` is not advanced by this pipeline.
- Development fixtures under `tests/reference_data/` are not experimental data.
- Experimental comparison only. Does not set package validation_status to 'independently_validated'. Synthetic smoke-test rows are not evidence.

## Row results

| scenario_id | status | force_definition | model F (N) | exp F (N) | abs rel err | synthetic |
|---|---|---|---|---|---|---|
| allm2014_gly_mu5_Q0p05 | compared | fluid_only | 7.231314415734038 | 10.38 | 0.3033415784456612 | False |
| allm2014_gly_mu5_Q0p1 | compared | fluid_only | 14.462628831468075 | 18.4 | 0.21398756350716977 | False |
| allm2014_gly_mu5_Q0p2 | compared | fluid_only | 28.92525766293615 | 23.27 | 0.24302783252841217 | False |
| allm2014_gly_mu10p5_Q0p05 | compared | fluid_only | 15.185760273041481 | 16.38 | 0.07290840823922576 | False |
| allm2014_gly_mu10p5_Q0p1 | compared | fluid_only | 30.371520546082962 | 36.4 | 0.1656175674153032 | False |
| allm2014_gly_mu10p5_Q0p2 | compared | fluid_only | 60.743041092165925 | 58.27 | 0.0424410690263587 | False |
| allm2014_gly_mu20_Q0p05 | compared | fluid_only | 28.92525766293615 | 28.38 | 0.019212743584783355 | False |
| allm2014_gly_mu20_Q0p1 | compared | fluid_only | 57.8505153258723 | 51.4 | 0.1254964071181382 | False |
| allm2014_gly_mu20_Q0p2 | compared | fluid_only | 115.7010306517446 | 93.27 | 0.24049566475549058 | False |
| allm2014_gly_mu48_Q0p05 | compared | fluid_only | 69.42061839104676 | 73.38 | 0.053957230975105436 | False |
| allm2014_gly_mu48_Q0p1 | compared | fluid_only | 138.84123678209352 | 121.4 | 0.14366751879813436 | False |
| allm2014_gly_mu48_Q0p2 | compared | fluid_only | 277.68247356418703 | 248.27 | 0.11846970461266776 | False |


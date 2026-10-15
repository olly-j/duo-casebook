# CASEBOOK Release Management

Status: Active release authority

## State model

- Source-ready: the feature branch is coherent and Lane C passes locally.
- Merge-ready: final diff and evidence are reviewed against CB-001.
- Deployed: GitHub Pages reports the `main` commit as built.
- Publicly verified: CASEBOOK identity, exact catalogue revision, image completeness and hosted browser journeys pass.
- Shipped: the owner accepts the publicly verified revision.

A commit or successful Pages build does not prove the public catalogue matches the source. Run `python3 scripts/verify_deployment.py` after deployment.

## Current release

- Work item: CB-001
- Target: `main`, GitHub Pages from `/docs`
- Scope: complete product visuals, gallery provenance, mobile UI/UX polish and core/web development-spine adoption.
- Approval: owner explicitly authorised implementation and public deployment on 15 October 2026.
- Evidence: `QA.md`, `research/catalogue-summary.json`, Lane C output and strict deployment verification.
- GitHub Release: deferred because this is a continuously published static catalogue without a packaged consumer artifact.

## Rollback

Revert the release commit on `main`, push the revert, wait for Pages to build, then run strict deployment verification against the restored catalogue. Preserve the failed revision and evidence for diagnosis.

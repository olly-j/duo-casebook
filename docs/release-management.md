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

- Work item: CB-002
- Target: `main`, GitHub Pages from `/docs`
- Scope: crawlable case pages, discovery metadata, sharing previews, Apple-inspired design, revised copy, image delivery and disabled consent-gated AdSense integration.
- Approval: owner explicitly authorised implementation and public deployment on 15 October 2026.
- Evidence: `QA.md`, `research/catalogue-summary.json`, Lane C output and strict deployment verification.
- GitHub Release: deferred because this is a continuously published static catalogue without a packaged consumer artifact.

## Rollback

Revert the release commit on `main`, push the revert, wait for Pages to build, then run strict deployment verification against the restored catalogue. Preserve the failed revision and evidence for diagnosis.

## CB-002 release acceptance

The owner requested production publication of this public site and tasteful advertising. That authority covers this bounded release; it does not activate publisher accounts, accept terms, provide payment details or waive consent/site approval. Advertising remains off. Physical iPhone and VoiceOver acceptance are not implied by emulated browser checks. Search Console submission and indexing are not claimed.

Public verification must match the exact build-manifest.json and its complete file inventory. Docs-only evidence reconciliation after publication must leave that inventory byte-identical.

## CB-003 second release

- Authority: owner requested a second, separate public release after the verified CB-002 deployment.
- Scope: root ads.txt and publisher meta (separate GitHub repository), complete site-wide privacy controls, tested local shortlist clearance, fail-closed Google CMP bridge and publisher readiness assessment.
- Public ads status: disabled. External AdSense site/publisher approval, genuine Google consent message and manual unit creation are independently required. Publisher information entered is not proof of site approval.
- Release evidence: source `./dev verify --lane C`, privacy browser/Axe tests, exact public manifest and all-file hashes, host-root ads.txt and meta, no premature third-party ad calls.
- Rollback: revert the CB-003 merge, redeploy Pages and verify the previous inventory; the separate publisher root has its own Git commit and independent rollback.

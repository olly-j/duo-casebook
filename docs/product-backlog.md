# CASEBOOK Product Backlog

Status: Active authority for scope, priority, owner decisions and release intent

Stable IDs use `CB-NNN` and are never reused. AI recommendations remain advisory until the owner approves priority, disposition or release.

## CB-001 · Complete visual catalogue and production-quality decision journey

- Owner review: Approved for implementation and public deployment, 15 October 2026
- Status: Release candidate
- Outcome: Every product entry has a truthful, source-linked visual and the mobile catalogue feels calm, useful and finished.
- Acceptance criteria: complete image provenance; exact product or explicitly labelled family/concept visuals; unnamed waitlists kept in the registry; working search, filters, matching, shortlist and 2 to 4 way comparison; no page overflow at supported widths; progressive details; accessible feedback; adopted core/web spine; Lane C and public verification pass.
- Non-goals: live stock promises, currency conversion, fabricated brand ratings, generated product imagery, automatic purchasing or an always-on monitoring service.
- Impact and lane: Lane C. Public catalogue, data contract, UX, governance and deployment all change.
- Evidence required: catalogue audit, image load audit, logic tests, real-browser interactions, viewport screenshots, exact public catalogue hash and deployment identity.
- Cost/runtime impact: no runtime dependency or recurring service cost; browser QA uses existing local tooling.
- Rollback: revert the release commit and let GitHub Pages redeploy the previous `docs/` revision.
- Release target: GitHub Pages after owner-authorised merge to `main`.

## CB-002 · Ongoing market refresh

- Owner review: Pending
- Outcome: Recheck new cases, availability, prices and independent Duo reviews on an agreed cadence.
- Trigger: owner chooses a cadence or the catalogue becomes materially stale.
- Guardrail: source-reviewed pull requests; no silent automatic publication.

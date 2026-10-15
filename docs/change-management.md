# CASEBOOK Change Management

Status: Active policy and current change record

Every implementation records a stable work ID, outcome, acceptance, non-goals, risk lane, affected surfaces, evidence, rollback and remaining human gates. Never weaken a check to make a release pass.

## CB-001 assessment

- Outcome: complete photo provenance and a polished decision journey.
- Lane: C, because public product data, UX, governance and deployment change together.
- Code impact: `web/`, `build_data.py`, publishing scripts and browser tests.
- Data impact: image galleries and provenance fields; unnamed CASETiFY waitlist removed from the product grid; QDOS placeholder replaced by its named Hybrid SNAP product.
- Privacy: no account, analytics or server-side user data. Shortlists remain local to the browser. External source images disclose normal image requests to their hosts.
- Security: HTTPS-only external images and links; safe relative image allow-list; escaped source text; no runtime third-party script.
- Accessibility: keyboard dialogs, focus restoration, 44px targets, mobile input sizing, status feedback, internal comparison scroll and reduced motion support.
- Performance: remote images remain lazy; no framework or runtime dependency added.
- Evidence: `./dev verify --lane C`, photo load audit, viewport screenshots and strict deployed-catalogue verification.
- Rollback: revert the release commit on `main`; GitHub Pages redeploys the previous `docs/` tree.
- Human gate: the owner explicitly authorised implementation and deployment in the current task.

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

## CB-002: Public launch, discovery, copy and responsible advertising

Owner request, 15 October 2026: make CASEBOOK discoverable and useful through search and sharing, apply an Apple-inspired iOS 27 design, use the supplied writing system, and add tasteful publisher advertising. Lane C. Existing authority covers bounded implementation, review and public deployment.

Acceptance: crawlable case pages with useful content without JavaScript; accurate metadata and sharing previews; source-derived copy and visible research date; preserved filtering, saved items and comparison; responsive light/dark design and accessibility preferences; complete image provenance; repeatable quality and exact hosted revision tests. Advertising remains off until an active publisher account, real ad unit, site approval and certified consent setup are verified. No ad calls before required consent. No pop-ups or ads inside ranking/comparison controls.

Non-goals: paid ad campaigns, payment details, account creation or binding terms, analytics, background watchers, domain changes, native conversion or another project's modification. Indexing, audience growth, physical device acceptance and AdSense approval are external outcomes, separately evidenced. Rollback: revert the integration commit and redeploy the last verified Pages tree.

## CB-003: Publisher root, privacy preferences and certified consent readiness

- Owner instruction: 15 October 2026. Release after CB-002. Improve privacy/cookie controls, start AdSense review, support UK/EEA/Switzerland consent while keeping the experience restrained. Owner permits publishing and account setup.
- Outcome: an accessible Privacy & cookies control across CASEBOOK; real origin ads.txt and account verification meta; certifiable, consent-before-ad gated Google CMP integration; a visibly clear separation between approved live ads and readiness scaffolding.
- Acceptance: local-only favourites and voluntary deletion; no fabricated opt-in banner when ads are disabled; a certified Google CMP, when approved and configured, owns equal Consent/Do not consent/Manage options; ads blocked on denial, missing API, wrong site, missing approval or withdrawal; privacy/method/source copy updated; verified public deployment with no ad requests before approval. Never invent Google approval.
- Non-goals: manufactured CMP certification, marketing revenue guarantee, cookie consent stored as a plain localStorage flag, personal-data collection, Google Ads purchase, forced monetisation or payment details.
- Lane C: account/CMP/external hosting plus shared UX; review exact official source and tests, separate deployment and published-state evidence.
- Dependencies: Google external site and account approval, certified CMP configuration, approved real ad-unit IDs; root ads.txt and meta can be made ready immediately. Owner to complete any interactive contractual or identity verification.
- Rollback: revert CASEBOOK CB-003 release and, if the publisher root changes, revert that root commit independently; keep public source evidence.

## CB-004: AdSense activation after external approval

- Owner-review state: external approval pending. [Tracked as GitHub issue #3](https://github.com/olly-j/duo-casebook/issues/3).
- Technical work: CB-003 publishes the dormant consent bridge, responsive privacy controls and verified publisher-origin metadata/ads.txt.
- Google state at last check: publisher onboarding still requires site connection; the payment-information card is complete but site approval is unverified. A certified, published Google Privacy & messaging European regulations message, exact CMP identifiers and real manual ad-unit configuration are pending.
- Activation invariant: never set `enabled:true` until account/site/CMP/consent network tests and privacy disclosures pass. Use a separate reviewed release. No fabricated consent, purchased traffic or intrusive advertising.
- Rollback: revert the activation PR or set ads back to disabled and verify network silence. Preserve evidence.

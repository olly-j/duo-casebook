# CASEBOOK launch evidence, CB-002

Research checked: 15 October 2026. Candidate catalogue: 92 entries across 44 brands, with a 67-brand discovery registry.

## Delivered features

- 92 of 92 case entries have source-attributed product visuals and two sizes of uncropped local WebP previews. Original image-source links remain accessible.
- The catalogue and 92 individual case pages work without JavaScript. The generated site includes a buying guide, method and privacy pages, 96 sitemap routes, original sharing art, canonical metadata and a hash-based public asset inventory.
- The interactive site supports filtering, favourites, search, sharing and comparisons. Light and dark themes, reduced-motion settings and responsive layouts are included.
- All 92 case summaries were reviewed; 46 were edited while preserving source facts.
- AdSense requests are OFF. AdSense account readiness, certified CMP and live ads require separate verification.

## Candidate evidence

- Development spine Lane C completed: Python and JavaScript unit tests, Chromium journey checks, layout and photo audits and source-data checks passed.
- 33 browser checks at five widths in both light and dark themes passed. Five sampled axe WCAG AA scans had no detected violations. No unexpected advertising requests were observed.
- Lighthouse simulated mobile, local candidate: performance 84, accessibility 100, best practices 100, SEO 100, LCP 4.4s and CLS 0.

## Publication gate

After GitHub Pages reports the merged commit built, verify the exact hosted build manifest and every file, then repeat the live browser matrix. Record actual public verification separately from candidate checks.

## Boundaries

These are lab measurements, not proof of physical iPhone or VoiceOver acceptance, search indexing, market completeness or real-world performance. Confirm current prices and availability at original sellers. Source images and third-party services can change. Root ads.txt and robots.txt are outside this project path.

## CB-003: privacy and AdSense readiness, 15 October 2026

**Source-ready candidate.** This is the owner's requested second publication, following CB-002. The public publisher-root project is independently deployed at `https://olly-j.github.io/`. Both the root entry page and root `ads.txt` returned HTTP 200, with the intended public publisher verification meta tag and Google declaration. The root project has its own Git and rollback boundary.

Site-wide **Privacy & cookies** opens an accessible native dialog. It accurately describes browser-local saved cases and inactive optional advertising, links to the privacy notice, and offers confirmed, narrowly scoped deletion of the user's saved cases. The reading pages work without JavaScript and retain their static privacy link. No fake Consent/Reject interface is shown while there are no optional ads to consent to.

When the owner separately obtains an approved AdSense site, actual ad-unit IDs and a published Google-certified Privacy & messaging European regulations message, the reviewed integration can pass genuine Google IAB TCData from its CMP to the conservative, single-placement loader. The interface to accept, decline, configure and withdraw must be the actual certified Google message. The code never stores a fabricated TCF consent flag, and is disabled by default in the public release.

**Candidate verification completed:** 184 frontend, advertising, privacy and CMP/bootstrap unit tests passed. Sixty Python source, discovery, readiness and development-spine tests passed. The full Lane C release suite passed in the candidate worktree. Privacy was tested in real Chromium at 320, 390 and 430 pixel widths in both appearances. It opened and closed with keyboard Escape, supported cancelled and confirmed shortlist deletion, preserved unrelated localStorage data, and worked on individual cases, the guide, About and Privacy. The sample axe privacy-dialog scan found zero WCAG A/AA violations. No unwanted Google advertising network requests or uncaught JavaScript errors were observed in this disabled configuration. Existing photo, responsive, search and comparison checks also passed.

**External limits:** The signed-in Google AdSense onboarding page still showed **Connect your site to AdSense** as required when checked, although the payment information card was complete. The site has not been confirmed approved or earning; Google review, CMP message publication/certification pairing and ad-unit creation are external gates. A source code test cannot establish account activation, genuine user consent, or a legal compliance guarantee. The Google-certified message itself cannot be browser-verified until Google authorises and publishes it. Actual mobile Safari/VoiceOver remain to be checked on physical devices. No advertising activation is claimed or simulated.

**Release verification:** after merging, confirm the specific GitHub Pages commit succeeded, compare the hosted `build-manifest.json`, verify every public asset and the root `ads.txt`, then run the privacy/site browser tests against the public URL. Record these findings in the merged PR discussion. Revert the second-release commit if site or consent controls regress; the publisher-root repository has a separate rollback.

## CB-005 design and interaction regression

- User request: classical Apple-like monochrome colours, iOS-style Liquid Glass for controls and menus only, with minimal latency and no artificial gloss on product content.
- Source references: Apple Liquid Glass HIG and Materials, naughtyduk/liquidGL v3.0.0 MIT source, blob SHA `b76e6872bf1c93ecacff646d09a77f5ce5f24ddb`.
- Planned checks: new `tests/liquid-ui.test.cjs` covers token palette, photo-layer exclusion, accessibility/data-saver guards, local lazy library URL and destruction after tray hide. Existing source and product tests continue in CI.
- Public acceptance must re-run the exact deployment verifier and hosted interface checks. No physical iOS/Safari FPS claim is made from source or simulated browser tests. The GPU renderer is disabled entirely on iPhone and Safari by deliberate policy, with the CSS-only material as the production fallback.

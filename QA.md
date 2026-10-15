# CASEBOOK Release Evidence

Research snapshot: 15 October 2026. Release candidate: 92 product-grid records across 44 brands, with 67 brands in the discovery registry.

## Catalogue and imagery

- 92 of 92 product entries have a primary visual, caption, image source and gallery record.
- 139 gallery records are present.
- Real Chromium loaded all 92 primary images: 0 missing and 0 broken during the release audit.
- Exact product photography is used where available. Retailer, concept and representative family visuals are labelled in their captions and provenance.
- The unnamed CASETiFY waitlist remains in the discovery registry rather than appearing as a case product.
- The former QDOS placeholder is replaced by the source-backed Hybrid SNAP product.

## Automated and browser evidence

- 17 focused frontend logic and accessibility-contract tests pass.
- 19 real-browser interaction checks pass, covering search, currencies, null measurements, front-only classification, matching, shortlists, four-way comparison, shared views, mobile filters, empty states, dimensions and uncaught errors.
- Layout checks at 320, 390, 430, 768 and 1440 pixels render all 92 records without page-wide horizontal overflow.
- Phone home, catalogue, filter and comparison views were visually inspected.
- `./dev verify --lane C` passes the complete logic, browser, viewport, image and release audit matrix.
- `python3 scripts/casebook_quality.py --mode release` passes with complete photo provenance.

## Public verification

After merge and Pages deployment, run `python3 scripts/verify_deployment.py` and the browser matrix with `CASEBOOK_TEST_URL` set to the public URL. Public verification must confirm CASEBOOK identity, the exact catalogue hash, 92 records, complete image provenance and no hosted browser errors.

## Boundaries

Chromium viewport emulation is not physical iPhone testing. Safari, VoiceOver, physical-device performance and independent case durability remain unverified. Remote source images can later move or fail; the UI retains a labelled fallback and the photo audit exposes breakage.

Source evidence and uncertainty remain visible. This snapshot cannot guarantee exhaustive worldwide inventory, future announcements, live stock or manufacturer measurement accuracy.

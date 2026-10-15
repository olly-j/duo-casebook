# Release checks

Research snapshot: 15 October 2026. Catalogue: 93 records, 45 product brands, 67 brands in the discovery registry.

## Automated checks

All 10 focused logic tests pass. The real Chromium interaction suite passes all 19 checks covering search, currency isolation, null measurements, front-only classification, the preference matcher, saved shortlists, four-way comparison limits, shareable comparisons, mobile filter sheets, empty states and closed-depth filtering. No uncaught JavaScript errors were recorded.

Real-browser layout checks at widths 320, 390, 430, 768 and 1440 pixels rendered the complete catalogue without page-wide horizontal overflow. Visual previews were inspected for the phone home and catalogue views.

The same functional and responsive suites have been exercised against the public GitHub Pages deployment. Test scripts are supplied so the hosted checks can be repeated after updates.

## Boundaries

Chromium viewport emulation is not physical iPhone testing. Safari, VoiceOver, physical device performance and independent case durability have not been verified. Manufacturer photography can be unavailable or change at source; missing images have a labelled fallback.

Source evidence and publication uncertainty are preserved inside each product record. A source-backed catalogue is not a guarantee of exhaustive worldwide inventory, future announcements, live stock or manufacturer measurement accuracy.

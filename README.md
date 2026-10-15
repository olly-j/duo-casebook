# CASEBOOK

A source-led, mobile-first iPhone Duo case catalogue.

**Open the app:** https://olly-j.github.io/duo-casebook/

The 15 October 2026 research snapshot contains 93 case designs, configurations and preview entries across 45 brands, with a 67-brand discovery registry. Counts are derived from `web/catalogue.json` and will change with subsequent research.

## Use

Search by brand, material, finish or feature. Refine by construction, protective hinge cover, MagSafe, stand, card storage, strap compatibility, price currency, case weight, wall thickness, published closed dimensions, availability and evidence. Save a shortlist locally, compare up to four records, or use the preference matcher. Filters and comparisons can be shared by URL. JSON and CSV exports are available in Research notes.

## Evidence and scope

Every product links to its source. Manufacturer claims, retailer listings, announcements and concepts are separated. The index covers publicly discoverable records; unannounced products, unindexed sellers and subsequent changes cannot be guaranteed. Decorative colours are grouped where practical. Functional configurations and front-only components remain clearly labelled.

Unknowns are null. Case weight excludes the phone. Magnetic force, package weight, side-wall thickness and total closed-device depth are distinct. A flexible hinge film does not qualify as a structural protective hinge cover. Prices retain their source currency and are not assumed to include UK delivery or import costs. No currency conversion is applied.

Historical hands-on reviews concern explicitly named previous models. They do not establish Duo performance or a company-wide quality score. Review sponsorship uncertainty, conflicting claims and limitations remain visible. The preference matcher ranks published attributes; it does not invent review ratings or product endorsements.

This is a dated snapshot. No automatic monitoring, background refresh, analytics, login or affiliate tracking is enabled. Shortlists stay in the browser. Product images are requested directly from their source hosts and remain their owners' work.

## Maintain

Edit dated evidence in `research/`, preserving exact source URLs and uncertainty. Run `python3 build_data.py` to validate and rebuild the catalogue, then `python3 prepare_site.py` to generate the GitHub Pages directory. The public app uses vanilla HTML, CSS and JavaScript with system fonts and no build dependencies.

Run logic checks with `node --test tests/polish.test.cjs`. Browser tests require Playwright. Set `PLAYWRIGHT_MODULE` and `CHROME_PATH` when using an existing local installation, and optionally `CASEBOOK_TEST_URL` to test a deployed URL. Browser emulation is separate from physical iPhone and Safari testing.

Only `docs/` is served by GitHub Pages. Synthetic test fixtures are excluded from deployment. Research and code are kept separate so updates can be reviewed without rewriting the interface.

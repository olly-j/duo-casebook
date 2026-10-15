# CASEBOOK

A source-led, mobile-first iPhone Duo case library for discovering, filtering, shortlisting and comparing the public market.

**[Open CASEBOOK](https://olly-j.github.io/duo-casebook/)** · **[Source repository](https://github.com/olly-j/duo-casebook)**

## Snapshot

The 15 October 2026 release contains 92 case designs, functional configurations and source-published concepts across 44 product brands. The discovery registry records 67 researched brands, including unnamed waitlists that are deliberately excluded from the product grid.

Every product entry has a provenance-linked visual. The catalogue contains 139 gallery records, including exact manufacturer imagery, clearly attributed retailer photography, labelled concept renders and explicitly labelled representative family photography for made-to-measure sleeves. CASEBOOK never generates a substitute product image.

## What it does

- Searches brand, case, material, finish, feature and colour.
- Filters construction, structural hinge protection, MagSafe, stand, card storage, straps, UK listings, availability, source confidence, brand-review evidence, price currency, case weight, wall thickness and published closed dimensions.
- Preserves unknown values rather than treating them as zero or false.
- Saves a local shortlist and compares two to four products with an internally scrolling phone layout.
- Shares exact filter and comparison views by URL.
- Uses a preference matcher based on published attributes, without invented review ratings or product endorsements.
- Exposes original sources, caveats, previous-model review evidence and image provenance through progressive detail sections.

## Evidence rules

Product claims remain tied to their manufacturer, retailer or announcement source. Case weight excludes the phone. Package weight, magnetic force, wall thickness and closed-device depth are separate fields. A flexible hinge film does not qualify as a structural hinge cover. Front-only and back-only components remain visibly distinct from complete protection. Prices keep their source currency and do not imply UK delivery, tax, duty or live stock.

Historical hands-on reviews concern the named previous model tested. They do not establish Duo performance or create a company-wide quality score.

## Architecture and privacy

CASEBOOK is static HTML, CSS and JavaScript served by GitHub Pages from `docs/`. It has no backend, account, analytics, affiliate tracking or runtime package dependency. Shortlists stay in localStorage. Shared views use URL parameters. Product images load from their recorded source hosts.

Authoritative product evidence lives in `research/` and is compiled by `build_data.py`. `web/` is the authored application. `prepare_site.py` creates the public `docs/` tree.

## Development spine

CASEBOOK adopts the `core` and `web-backend` profiles from `olly-j/ai-development-spine`, tracking `main` through reviewed project-specific changes. The resolved adoption revision is recorded in `.spine/manifest.json`; updates never auto-merge.

```bash
./dev orient
./dev audit
./dev verify --lane A   # focused logic or copy
./dev verify --lane B   # user-facing behaviour and browser interaction
./dev verify --lane C   # publication, complete viewport and photo matrix
./dev release-plan      # read-only release and deployment state
```

Start with `AGENTS.md` and `docs/README.md`. The canonical work record is `docs/product-backlog.md`; release evidence is in `QA.md`.

## Refreshing the catalogue

1. Update dated source records under `research/`, preserving exact URLs and uncertainty.
2. Run `python3 build_data.py`.
3. Run `python3 prepare_site.py`.
4. Run `./dev verify --lane C`.
5. Review the diff, merge with owner authority, wait for Pages, then run `python3 scripts/verify_deployment.py`.

Rollback is a Git revert of the release commit followed by strict public-deployment verification.

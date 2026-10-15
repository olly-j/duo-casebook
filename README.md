# CASEBOOK

[Open the iPhone Duo case finder](https://olly-j.github.io/duo-casebook/)

Compare case coverage, materials, source-currency prices and published measurements. Save a shortlist in your browser, compare up to four cases and share a case or filtered view. Every product links to its original sources and photographs.

## Find a case

The 15 October 2026 research snapshot includes 92 case designs and configurations across 44 product brands. The discovery register covers 67 brands. Decorative finishes are grouped where they share a design; front-only parts, back-only shells, full sets and concepts remain distinct.

The [buying guide](https://olly-j.github.io/duo-casebook/guides/choose-a-case/) explains coverage, measurements and buying terms. Each case also has a readable, shareable page that works without JavaScript. Filtering, saving and comparison use the enhanced catalogue.

## Sources and trust

Manufacturer descriptions remain manufacturer claims. Historical reviews identify the exact older model tested. CASEBOOK has not physically tested these Duo cases and does not invent review ratings, global rankings or unpublished specifications. Confirm live stock, the selected variant and delivered total with the seller.

Sources were checked on the displayed date. Page modification dates do not imply fresh price research. No background monitoring is running. Corrections can be reported through this repository's Issues without posting private order details.

Original photography stays attributed. Source-derived WebP delivery copies improve loading without cropping, generating or retouching product content. Full source references remain available.

## Advertising and privacy

Google AdSense is configured but **disabled** until the publisher account and site approval are confirmed. The accompanying [publisher-root repository](https://github.com/olly-j/olly-j.github.io) now serves the origin-level `ads.txt`, ownership verification meta and an accessible CASEBOOK entry page. The [Privacy & cookies](https://olly-j.github.io/duo-casebook/privacy/) control explains the current browser-local shortlist and can clear it without affecting unrelated storage.  Activation requires verified publisher and site approvals, real ad-unit IDs, a reviewed certified consent provider and host-level ads.txt. The shipped build makes no advertising or analytics requests. Any future placement is labelled and separated from case order and comparisons. No ad-serving account activation, payment change, tracking service or paid advertising campaign was performed. The previously existing account displayed payment information received, while Google still requires site connection and review.

Saved cases use browser-local storage. The Privacy & cookies control is available throughout the site and links to the [privacy notice](https://olly-j.github.io/duo-casebook/privacy/). When a Google-certified consent message is approved and configured, that message will handle equal Consent, Do not consent and Manage options and withdrawal. No nonessential advertising request may be made before valid consent. A local checkbox is never treated as IAB consent.

## Develop and verify

Read [AGENTS.md](AGENTS.md) and the [authority map](docs/README.md). The project adopts the core and web profiles of the owner's AI development spine. Native iOS APIs and portfolio controls are outside this static site's scope.

```sh
./dev orient
python3 build_data.py
python3 prepare_site.py
./dev audit
./dev verify --lane C
```

Python 3 and Node run the offline contracts. Browser checks reuse an existing Playwright, Chromium and axe-core installation, located by the runner or supplied through PLAYWRIGHT_MODULE, CHROME_PATH and AXE_PATH. No package installation occurs implicitly. The lightweight GitHub workflow runs offline checks and a deterministic rebuild.

`research/` holds source facts, editorial patches and image-delivery provenance. `scripts/adsense_readiness.py` is a read-only publisher readiness audit. `web/google-cmp-provider.js` and `web/privacy-center.js` implement distinct certification and user-experience boundaries. `web/` holds authored interface assets. `scripts/build_discovery.py` generates crawlable case and editorial pages. `docs/` is the Pages deployment tree and also retains Markdown project authorities. The build copies only explicit public assets. It never publishes agent logs, Apple guidance exports or private account evidence.

## Release

Review the pull request and [QA record](QA.md), then deploy the authorised commit through GitHub Pages. Run the strict public verifier:

```sh
python3 scripts/verify_deployment.py --all-files
```

It checks the exact build inventory and every published file, not only a successful HTTP response. Revert the release commit to roll back. Search inclusion, traffic, AdSense approval and physical iPhone/Safari acceptance remain external outcomes; lab scores do not guarantee them.

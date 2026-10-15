# CB-002 static discovery

The source catalogue remains `research/*.json` plus `build_data.py`. This builder reads the resulting `web/catalogue.json`; it never edits product facts or `web/index.html`.

## Build contract

Parent integration runs `build_discovery(root: Path, output: Path)` from `scripts/build_discovery.py` **after** copying public `web/` assets to the deployment directory. CLI: `python3 scripts/build_discovery.py`, default output `docs/`; `--output PATH` supports isolated review output. The builder writes generated HTML, sitemap, project-path robots artifact, reading assets and a manifest. It preserves existing authority Markdown. It does not copy research, agent notes, private guidance or repository configuration.

The source should delimit the contents of the product grid with `<!-- CASEBOOK_STATIC_START -->` and `<!-- CASEBOOK_STATIC_END -->`. Fallback accepts `div#products` or `div#results`, preserving the surrounding element and matching nested divs. Marker placement inside `#products` preserves app controls and lets existing JavaScript replace the first-class static cards normally. Each card links to its case page and exposes `data-detail`, `data-save` and `data-compare` controls. Static pages stay usable if JavaScript is disabled or catalogue data fails.

The public canonical base is `https://olly-j.github.io/duo-casebook/`. Current data produces 92 case pages, home, one guide, about and privacy: 96 indexable URLs plus a noindex 404. Case content includes source images and attribution, specs, explicit unknowns, variants, caveats, research dates, source facts and previous-model brand evidence. App links use `?case=ID` and `?compare=ID`; a single comparison selection is a starting point for adding others in the app. Multiple selections use repeated `compare` parameters, matching the application contract.

## Metadata and evidence boundaries

Every page has its own title, description, canonical and Open Graph URL. JSON-LD uses root WebSite and CollectionPage/ItemList, basic Product on case pages, and BreadcrumbList. No offers, review, aggregateRating or invented availability are emitted. Basic Product markup does not claim Google product rich-result eligibility. No ranking, indexing, AI inclusion or sharing-preview outcome is guaranteed.

Research dates are displayed as research dates. Sitemap `lastmod` records the UTC time generated HTML actually changed, preserved from the previous sitemap when its content hash is unchanged. The prior build manifest allows this to survive the parent's asset-copy step. A first generation establishes the first known page modification time; it does not assert an earlier publication date. Editorial content changes therefore have their own modification times rather than borrowing catalogue research dates.

`robots.txt` here is a **project-path artifact** at `/duo-casebook/robots.txt`. Crawlers consult the origin's `/robots.txt`; this file does not control `olly-j.github.io`. Do not claim that a repository subpath robots file governs the host. Sitemap submission and Search Console verification remain external work, not an effect of generating these files.

`build-manifest.json` contains sorted SHA-256 hashes of deployed HTML/CSS/JS/JSON/XML/TXT/SVG/PNG, excluding itself and hidden paths. It is deterministic for identical output bytes, without a fresh-build timestamp. Parent should call `write_manifest(output)` after any subsequent deployed-asset mutations. It is a byte inventory, not a permission to publish every file found in an existing output directory. Parent owns the public copy allow-list.

## Editorial and interaction brief

Reader: a UK-oriented iPhone Duo buyer on a phone. Prior knowledge: partial case specifications and uncertainty about coverage. Outcome: distinguish coverage, interpret measurements and delivery terms, then shortlist comparable cases. Literal ask: browse, compare and check the original seller. Medium: static pages with concise introductions and as much source-backed reference detail as needed. Register: plain, specific and friendly.

Familiar navigation, normal links, grouped specifications and visible unknowns aim to reduce recall and comparison effort. They remain design hypotheses. Reading CSS uses shared colour variables with fallbacks, system fonts, visible focus, minimum-height navigation/actions, reduced-motion rules and narrow-screen specification stacking. Parent supplies browser, zoom, screen-reader and device evidence; automated structure checks cannot establish those outcomes.

Privacy text reflects current account-free, analytics-free operation, browser-local favourites, URL selections, external image requests and GitHub hosting. Advertising is currently off. Parent should reconcile the wording if operation changes. Guide alone includes a hidden article placement after useful content; case, privacy, about and 404 pages have no ad slots. Home and guide include ad assets only when all three supplied assets exist, without duplicating includes. Advertising activation and certified-CMP integration remain owned by the ads/parent work; reading.js deliberately introduces no second state or consent system.

## Guidance consulted

Google's [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics) and [crawlable links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) support server-built content and normal anchor links. [Canonicalisation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls) informs consistent page URLs. [AI features](https://developers.google.com/search/docs/appearance/ai-features) adds no special AI file requirement. [Product snippets](https://developers.google.com/search/docs/appearance/structured-data/product-snippet) does not justify inventing offers or ratings. [Helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) informs source-backed decision detail. [Sitemaps](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap) informs canonical URL enumeration and truthful modification dates. These are lower-priority implementation references, not authority to expand scope.

## Validation and handoff

Run `python3 -m unittest discover -s tests -p test_discovery.py`. Tests build into isolated temporary directories; no generated `docs/` tree is written by the discovery engineer. Checks cover all 92 case pages, unique metadata, valid JSON-LD without fabricated commercial/review fields, product links, sitemap coverage/dates, internal anchor destinations, source preservation, repeated-build stability, unsafe IDs and URLs, script-close escaping and placement boundaries.

No packages, backend or recurring service are added. Rollback removes the six owned source/documentation files and parent build invocation, then rebuilds using the previous prepared-site path. Deployment or merge is outside this assignment.

## Launch integration

Home and guide share a locally rendered CASEBOOK preview image. All 92 products have original-source image references and optimised uncropped delivery copies. Browsing works from static HTML before enhancement, and the initial enhancement preserves those cards to reduce avoidable repaint. Product summaries were reviewed across all 92 records, with 46 source-preserving edits. Source dates stay distinct from page modification timestamps. Public indexing, traffic and preview caches remain external outcomes.

Origin-level robots.txt and ads.txt were not changed. This repository owns the /duo-casebook/ project path, not a root Pages site. Search Console ownership and sitemap submission require account confirmation; no ranking, indexing or AdSense approval is implied by technical validation.

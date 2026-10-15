# CASEBOOK Project Profile

Status: Active reference

Enabled profiles: `core` and `web-backend`.

## Product

CASEBOOK is a source-led, mobile-first iPhone Duo case catalogue for a UK buyer. It helps people discover, filter, shortlist and compare public case designs without inventing missing measurements or review scores.

## Architecture

- Static HTML, CSS and JavaScript hosted by GitHub Pages from `main/docs`.
- `research/*.json` plus `build_data.py` form the product-data authority.
- `web/` is the authored application; `docs/` is the prepared deployment tree.
- Public data contract: `window.CASEBOOK` and `catalogue.json`, schema version 1 by repository convention.
- No backend, database, API key, runtime package, account or analytics service.
- Shortlist state uses localStorage; share state uses URL parameters.
- Optimised product thumbnails and preview copies are served by the site. Original gallery images retain source URLs and attribution. Image resizing never changes product facts.

## Web boundaries

- Keep source-ready, deployed and publicly verified revisions distinct.
- A successful HTTP response is insufficient; deployment verification checks CASEBOOK identity and exact catalogue hash.
- No staging credentials exist because the product has no authenticated service. Feature branches and local file/browser testing provide the pre-production boundary.
- Deployment is the prepared `docs/` tree. Rollback is a Git revert to the last publicly verified revision.
- External links and images are treated as untrusted input. Source text is escaped before insertion.

## CB-002 publication extension

The prepared tree now contains crawlable case pages, an original buying guide, editorial method and privacy information. scripts/build_discovery.py generates 92 case pages from the same reviewed catalogue and an exact SHA-256 build inventory. No-JavaScript reading is supported. Native SwiftUI APIs are out of scope; Apple design guidance informs web typography, controls, materials and accessibility.

Optional publisher ads are disabled in the shipped configuration. scripts and hosts cannot activate until publisher, site and certified-consent gates are complete; the current site makes no ad-network or analytics requests. No third-party CMP or paid service was installed.

## CB-003 privacy/advertising design

The footer Privacy & cookies control is static-page and JavaScript compatible. Saved-case deletion explicitly removes only the catalogue's browser-local key. A Google-certified CMP is required for optional advertising; the adapter never fabricates or persists TCF consent. `google-cmp-boot.js` is inert until verified publisher, site, CMP, consent message, matching origin and valid script are all approved. The publisher root (`olly-j/olly-j.github.io`) owns Google verification meta and ads.txt, outside the catalogue project path. Publishing consent code does not mean Google approved the site or that ads are active.

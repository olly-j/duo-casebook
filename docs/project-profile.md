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
- Product images load from their recorded source hosts and retain source attribution.

## Web boundaries

- Keep source-ready, deployed and publicly verified revisions distinct.
- A successful HTTP response is insufficient; deployment verification checks CASEBOOK identity and exact catalogue hash.
- No staging credentials exist because the product has no authenticated service. Feature branches and local file/browser testing provide the pre-production boundary.
- Deployment is the prepared `docs/` tree. Rollback is a Git revert to the last publicly verified revision.
- External links and images are treated as untrusted input. Source text is escaped before insertion.

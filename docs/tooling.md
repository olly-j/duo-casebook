# CASEBOOK Tooling Decisions

Status: Active register

| Tool or service | State | Purpose and boundary | Cost / rollback |
| --- | --- | --- | --- |
| Vanilla HTML, CSS and JavaScript | Supported | Runtime application with no framework or third-party script | No recurring cost; edit or revert source |
| Python standard library | Supported | Catalogue build, quality audit, deployment verification and spine runtime | No project dependency install |
| Node test runner | Supported | Deterministic frontend logic and contract tests | No runtime dependency |
| Playwright with an existing cached Chromium | Supported for QA | Real-browser interactions, viewport captures and image-load audits | Development-only; scripts locate existing tooling or fail clearly |
| GitHub Pages | Supported | Public static deployment from `main/docs` | Existing public hosting; rollback by Git revert |
| AI Development Spine | Supported | Operating contract, risk lanes, evidence and portable `./dev` interface | Tracks `olly-j/ai-development-spine` main through reviewed project-specific changes |
| Remote source images | Supported with provenance | Exact product, retailer, family or concept visuals only | Source hosts may change; labelled fallback and audit expose failures |
| Automatic market monitoring | Not adopted | No background price or product watcher exists | Requires a separate owner decision and cadence |

Repository scripts protect stable invariants without becoming an exclusive tool allow-list. New runtime dependencies, recurring costs, external data collection or automatic publication require a reviewed CB work item and rollback.

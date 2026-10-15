# CASEBOOK GitHub Capabilities And Releases

Status: Active disposition

GitHub supplements the repository authorities. It does not replace product scope, evidence or release approval.

| Capability group | Disposition | Evidence or trigger |
| --- | --- | --- |
| GitHub Pages | Adopted | Public static site deploys from `main/docs`; strict verifier compares public catalogue hash with the prepared revision |
| Pull requests and issue forms | Adopted | Short-lived branches and CB work IDs provide reviewable scope; templates are included |
| GitHub Releases and tags | Deferred | No packaged binary or external API contract. Adopt when a durable consumer version or downloadable artifact needs a formal release |
| Branch protection / rulesets | Deferred | Single-owner public project. Reconsider with collaborators, higher traffic or automated deployment checks |
| Actions | Pages only | Native Pages deployment is active. No extra workflow or recurring CI cost is introduced in this change |
| Dependency and provenance automation | Not applicable today | Runtime has no third-party package. Reassess before adding dependencies or generated distributables |
| Secrets and environments | Not applicable today | No deployment credential or production secret is stored in the repository |
| CODEOWNERS | Deferred | Single owner; add when another maintainer joins |
| Projects and Discussions | Deferred | Repository docs remain the product authority; enable only when they reduce coordination drift |
| Commit signatures | Optional | Current evidence is commit SHA plus repository and public-deployment verification |

Public deployment and merge are human gates unless the owner explicitly delegates them for the current task. Automatic publication of AI-generated notes or releases remains disabled. Any future Action must use minimal permissions and a full commit SHA pin.

## CB-002 lightweight CI

The quality workflow now runs catalogue and deployment audits, 76 frontend/advertising checks, Python runtime/discovery tests and a deterministic rebuild on pull requests and main pushes. It uses a full-SHA-pinned checkout action, read-only repository permissions, cancellation of superseded runs and a five-minute timeout. Browser and visual release checks run locally against the exact deployment tree and are repeated against the public site. No paid service, account or new package was installed.

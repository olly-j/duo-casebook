# CASEBOOK Agent Instructions

This is the canonical operating contract for humans, ChatGPT, Codex, Claude
Code, GitHub Copilot, Gemini, and future tools. Tool-specific instruction
files may point here and add invocation details; they must not redefine policy.

## Authority And Conflicts

Apply instructions in this order:

1. the owner's explicit instruction for the current task;
2. this `AGENTS.md`;
3. the authority map in `docs/README.md`;
4. the relevant active policy or project profile;
5. archived evidence, which is context only.

When prose and implementation disagree, establish observed behavior first and
use a tracked owner decision to change intended behavior. Do not rewrite
evidence merely to make a conflict disappear.

## Least-Restrictive Effective Control

Use the least restrictive control that reliably protects the outcome:

- **Invariants** must remain true.
- **Required evidence** states what must be demonstrated.
- **Preferred defaults** are supported routes, not exclusive methods.
- **Experiments** may test better routes with success, cost, risk, and rollback
  criteria.

Repository scripts are mandatory when they verify an authoritative invariant
or synchronization boundary. They are not an exclusive tool allow-list.

## Capability Freedom And Proactive Improvement

Within the authorized task, humans and AIs may use available tools, skills,
agents, browsers, integrations, local automation, and platform-native
features. A capable tool does not need separate permission merely because it
was not known when these instructions were written.

Contributors should proactively recommend a better route when it can improve
user outcome, quality, accessibility, privacy, security, delivery time,
maintenance cost, cloud cost, or reversibility. State observations,
inferences, and recommendations separately.

Research and read-only evaluation are normally permitted. Installing a shared
dependency, introducing recurring cost, changing architecture/policy, or
mutating external/production state requires proportionate assessment and
owner approval.

Do not use these instructions as a reason to ignore useful native
capabilities. Do not use new capabilities to bypass scope, evidence, human
gates, or sources of truth.

## External Capability Precedence

External skills, personas, standards, registries, hooks, and tools are
replaceable inputs below this repository contract. Apply them in this order:

1. the owner's instruction for the current task;
2. this `AGENTS.md` and the repository authorities;
3. the project manifest, required evidence, and human gates;
4. spine-owned capability routing;
5. the smallest selected external workflow, persona, or reference.

Workflow skills define how to perform a task. Personas add a review
perspective. Standards describe a format. Hooks and installers execute code.
Do not collapse those roles, load an entire catalog when one capability is
enough, or let an external prompt approve scope, evidence, merge, deployment,
or release. New sources default off. Read-only discovery and drift reporting
may run autonomously; activation or self-modification must produce a pinned,
reviewable diff with normal evidence and rollback.

## Required Orientation

Before changing files:

1. read `docs/README.md` and the authorities for the affected surface;
2. run `./dev orient`;
3. inspect Git status, implementation, tests, and the stable work record;
4. read linked Issue and pull-request discussions when GitHub coordination is
   part of the task.

## Work Contract

1. **Orient:** identify the work ID, owner decision, affected authority,
   external state, and uncommitted user work.
2. **Define:** record outcome, acceptance criteria, non-goals, risk lane,
   impact, evidence, cost, and rollback.
3. **Implement:** make the smallest coherent change that fully meets the
   outcome; preserve unrelated behavior and work.
4. **Verify:** test logic, integration boundaries, failure paths,
   accessibility, privacy, security, and performance in proportion to risk.
5. **Reconcile:** update durable local and online records in the same task when
   their facts change.
6. **Review:** inspect the final diff for scope, secrets, unsupported claims,
   generated files, and avoidable complexity.
7. **Hand off:** report exact evidence, gaps, costs, risks, rollback, external
   state, and remaining decisions.

For work affecting user-facing journeys, interaction, navigation, forms,
onboarding, settings, feedback states, or other UX/UI behaviour, include
`docs/human-behaviour-ux.md` in the relevant design and review pass. Apply its
heuristics as hypotheses and starting points, then use accessibility checks,
experimentation, usability evidence, and measured outcomes to decide whether
the design works in context.

Never describe an unrun check as passing. Preserve baseline failure evidence
and use the smallest exact rerun to separate regression from environment.

## Lazy Freshness And Restart Continuity

Keep one approved outcome and next action. Use `./dev workflow active` and
`./dev workflow resume` for a compact local checkpoint; inspect existing results
before rerunning and checkpoint coherent tested work in Git promptly. References
are not proof, and a commit is not approval, merge or release.

Treat access, services, capacity and tool availability as live observations.
Expiry never schedules work. Probe the narrow needed capability at use or a
material decision, after a relevant fix, and before escalation/final claims.
The actual authorized operation can be the probe. Reuse fresh results, bind them
to execution/credential context, and never report a historical failure as a
current blocker. `live-status` and `resume` perform no network checks.

Reuse exact-source/configuration evidence through the project's verifier;
re-run changed inputs and final integrated gates, not unchanged work because a
session resumed. Two same-cause environmental failures call for diagnosis and
an already-approved alternative, not infinite retries or a weaker test. Keep
private runtime history out of routine context. No polling, extra status
repository, automatic fallback execution or additional recurring service.
Phase plans identify cycles; existing product, device and owner gates still
control approval. Read the project's authority before interpreting a gate.

## Change Lanes

- **Lane A:** surgical and readily reversible; focused checks.
- **Lane B:** bounded feature or shared behavior; integration, failure-state,
  and affected-journey evidence.
- **Lane C:** architecture, new platform/dependency/data use, cross-repository,
  costly, or high-risk work; discovery/decision, staged plan, wider matrix, and
  explicit owner approval.

Large changes are allowed. They receive proportionate assessment rather than
arriving as incidental edits.

## Apple Toolchain Skills

For iOS work, use the spine-owned Apple router at task admission, resume and use,
and at release boundaries. Default policy discovers the newest applicable locally
installed Xcode dynamically; no Xcode/SDK version or export is a template default.
Use bounded installation directories, Spotlight and optional configured roots;
never change global xcode-select, install tools or silently fall back on failure.
An explicit developer directory is an identified compatibility exception; require
latest when that exception is inappropriate. Channel eligibility needs metadata
or current official evidence; filenames and build numbers prove no channel.

`./dev apple-skills check` and `route` freshly export and verify before returning
usable paths. Offline inspection is explicitly offline and cannot establish
latest. New/changed guidance produces a concrete candidate/diff; the invoking
engineering agent reviews exact original guidance and applicability, adopts its
exact digest, then re-exports/bootstrap verifies before use. Owner authorization
to keep current covers this technical review; do not ask for approval of each
version again. New or renamed unknown skills require explicit applicability
review. A reviewed snapshot is provenance, never frozen selection policy.

Newest installed is not newest Apple-published. Only a bounded explicit current
official observation can support published freshness; absent network evidence
must remain explicit. Apple guidance stays below owner/repository authority,
evidence and human gates and grants no model, agent, helper-execution, security
setting or entitlement permission. No Apple bodies belong in Git without
redistribution licence evidence. Release readiness fails closed on discovery,
export, drift or missing evidence; non-iOS projects report `not_applicable`.
Preserve downstream decisions and legacy reviewed snapshots on updates.

## Human Gates

Explicit owner approval is required before production deployment/public
release, store submission, pricing, signing, entitlements, privacy
declarations, destructive external mutation, deletion/disposition of durable
evidence, new recurring cost/external authority, or PR merge unless delegated.

Planning, read-only audits, builds, tests, reviewable artifacts, and proactive
recommendations do not themselves cross these gates.

## Backlog, Feedback, And Documentation

- Planned work and owner decisions belong in `docs/product-backlog.md`.
- Raw feedback belongs in `docs/user-feedback.md` and is never deleted merely
  because it is old.
- Every implementation references a stable work ID.
- Only the owner approves priority, deferral, rejection, duplicate treatment,
  closure, archival, or shipped/released status.
- Update an existing authority before creating a competing document.
- Tool-specific files remain thin adapters to this contract.
- Do not commit disposable AI logs or status reports.

## Git And Review

- Use a short-lived branch linked to one stable work item.
- Preserve unrelated and pre-existing changes.
- Keep commits and PRs cohesive and reviewable.
- Use a PR for the integration branch; draft while evidence is incomplete.
- Do not force-push, rewrite shared history, merge, tag, release, deploy, or
  delete remote work without authorization.
- Never commit credentials, signing material, personal editor state, caches,
  or unreviewed generated artifacts.

Before handoff, run `./dev audit` and `./dev verify --lane <A|B|C>` plus any
stronger checks relevant to the task. Use `./dev evidence --lane <A|B|C>` as a
handoff skeleton.

Use `./dev ecosystem` to inspect the pinned capability catalog. Its optional
`--check-upstream` mode is read-only and reports review due; it never installs
or updates a source.

Use `./dev github-review` before the first public/versioned release and when
GitHub plan, visibility, team, release, deployment, or platform capability
changes. Its optional `--check-live` mode is read-only and never changes
repository settings. Apply `docs/github-capabilities.md`: a GitHub Release is
supplemental to canonical release truth, and publishing remains a human gate.

## Continuous Improvement

Run the process review quarterly, after material incidents, and when platform
capabilities, repository plan/visibility, team scale, or pricing change.
Prefer measured simplification over ceremony.
Every lasting control needs an owner, trigger, evidence, cost expectation, and
removal path.

## CASEBOOK Product And Data Invariants

- `research/*.json` and `build_data.py` are the product-data authority. `web/data.js`, `web/catalogue.json` and their `docs/` copies are generated artifacts. Never edit generated catalogue facts by hand.
- Every product shown in the catalogue must have a source URL, a provenance-linked primary visual, a non-empty image caption, an image source, and at least one gallery item. `python3 scripts/casebook_quality.py --mode audit` enforces this boundary.
- Use genuine source-published product photography or renders for the exact Duo family. Never generate a substitute product image. Never borrow an image from another phone model or another case.
- Representative family photography is permitted only for made-to-measure products, with the representation stated in the caption. Concept renders, retailer photography and bundle photos must also be labelled accurately.
- An unnamed waitlist, brand announcement or future lineup without a verifiable case visual belongs in the coverage registry, not the product grid.
- Unknown facts remain `null`. Package weight, magnetic force, phone dimensions, side-wall thickness and closed-device depth are separate quantities and must not be substituted for one another.
- A flexible hinge film does not satisfy the structural hinge-cover filter. Front-only and back-only components must remain visibly distinct from complete protection.
- Prices retain source currency. UK listing does not imply UK delivery, tax, duty or live stock unless the source establishes it.
- Historical reviews remain tied to the exact previous model tested. They do not create a numeric brand score or establish Duo performance.

## CASEBOOK Publication Boundary

GitHub Pages serves only `docs/`. Run `python3 build_data.py` and `python3 prepare_site.py`, then Lane C verification before publication. Keep source-ready, deployed and publicly verified revisions distinct in `docs/release-management.md`. Public deployment and merge require owner authority; an explicit owner instruction covering the current release satisfies that gate.

# CB-003 Google CMP bridge

Status: local adapter for review. Advertising remains off. There is no active
certified CMP, and publisher website verification is incomplete. This document
does not authorize activation or replace the advertising or privacy authorities.

## What this does

`web/google-cmp-provider.js` exposes
`CasebookGoogleCMP.create(window, document, config)`. It installs no external
script, banner, encoder, storage, timer or ad request. It uses the existing Google
Privacy & messaging callback queue and real `__tcfapi` only after configuration
gates pass. Missing APIs produce denial, with no polling or fallback bootstrap.

The actual consent interface must be Google's reviewed certified message, with
three equally prominent options: **Do not consent**, **Consent**, and **Manage
options**. This adapter creates no consent UI. Keep the original catalogue and
privacy information readable without JavaScript. A local preference boolean,
Consent Mode signal or TC string alone is not legal certification.

## Integration contract

The parent owns configuration, bootstrap, HTML, copying into `docs/`, and browser
verification. None are changed here. Load this local file before creating the
provider and pass the resulting object to the existing ads loader:

```js
const provider = window.CasebookGoogleCMP.create(window, document, reviewedConfig);
// Pass provider as consentProvider to CasebookAds.start(options).
// Keep the returned unsubscribe function for teardown.
const unsubscribe = provider.subscribe(signal => { /* process every signal */ });
// Call from an explicit user action only:
const opened = provider.openPreferences();
```

Do not create a redundant subscription merely to activate ads. Each subscription
owns one TCF listener and starts with denial. Updates have the existing shape
`{authorized, fullLegalBases, configId, success, tcData}`. Duplicate CMP events
are forwarded deliberately; consumers must be idempotent. No cached grant is
replayed to new subscribers. `success` reports the CMP callback result, while
both authorization fields remain false whenever validation fails.

Required existing configuration fields:

| Field | Required value |
| --- | --- |
| `enabled`, `publisherApproved`, `siteApproved`, `consentReady` | Strict `true`, backed by real evidence |
| `publisherId` | Real reviewed account identifier, never a fixture |
| `consentConfigId` | Nonempty identifier for the exact reviewed deployment |
| `approvedHosts` | Explicit list including the current host |
| `requiredPurposes` | Includes `[1,2,3,4,7,9,10]`, only integer purpose IDs 1 to 10 |

The additional `googleCMP` object must contain:

| Field | Required value |
| --- | --- |
| `reviewed`, `certifiedConfigurationReviewed`, `legalBasesReviewed` | Strict `true` after deployment-specific review |
| `publisherId`, `configId` | Exact matches to the existing fields |
| `approvedOrigin` | Exact HTTPS site origin |
| `approvedPath` | `/duo-casebook/`, including trailing slash |
| `allowedCmpIds` | Nonempty explicit list of reviewed IAB CMP IDs |
| `vendorListVersion`, `tcfPolicyVersion` | Positive integers pinned to the reviewed CMP/GVL configuration |
| `googleOnly` | Strict `true`, only vendor 755 in the approved ad-technology scope |
| `additionalConsentRequired` | Strict `false`, with no Additional Consent dependencies |

There are deliberately no real publisher IDs or default CMP allowlist here.
Do not copy test fixtures into deployment configuration. The reviewed flags are
local attestations, not cryptographic verification of Google accounts, identity,
certification or message settings. Review must establish the actual Google CMP
identity, current certification, vendor registration and disclosures, exact
publisher/site/message pairing, consent legal bases, and restricted technology
scope. Other vendors or Additional Consent dependencies require another reviewed
implementation; do not set flags to bypass them. GVL/policy changes deny until
the configuration is reviewed again. Inputs are snapshotted without mutation.

## Consent and withdrawal

Readiness uses the documented `CONSENT_API_READY` queue hook. Subscription uses
`__tcfapi('addEventListener', 2, callback)` and removal uses the returned
`listenerId`. A subscriber removed before readiness never registers; late events
cannot grant and allow deferred listener removal when its ID arrives.

Grants require a successful callback, loaded CMP, `tcloaded` or
`useractioncomplete`, `gdprApplies === true`, an allowlisted CMP ID, matching
GVL/policy versions, listener ID, plausible nonempty TC string syntax, vendor
755 consent, and explicit consent for every required purpose. Restrictions 0,
2, malformed restrictions or unknown states deny. Flexible Google purposes
2, 7, 9 and 10 must explicitly select consent with restriction 1. Other required
purposes accept no restriction or restriction 1. This intentionally adopts a
stricter consent-only route. Purpose 2 is required in addition to the old loader
minimum. No non-personalized or limited-ad fallback is implemented.

The adapter trusts the real CMP to produce and validate its TC string. It does
not decode, generate or cryptographically authenticate strings. Syntax checking
cannot establish validity, and forged globals cannot be authenticated by local
JavaScript. The `fullLegalBases` attestation is limited to this reviewed
Google-only, consent-only scope, not a finding of legal compliance.

Errors, partial TCData, UI-open events and refusals emit denial. GPC true denies
on every callback. There is no universal browser GPC change event; the ads loader
must continue checking GPC before delayed requests and pushes. No polling is
used. `gdprApplies === false` and unknown geography both deny. No non-EU override
ships; such a policy requires a separate explicit review and implementation.

`openPreferences()` returns false without readiness or the documented Google
method. After an active subscription has observed API readiness, it first emits
denial to all subscribers, then calls `googlefc.showRevocationMessage()`. Call it
only in response to a user action. A true return means invocation succeeded,
not that the UI was visually verified. Exceptions return false and keep denial.
There is no reload. Revocation cannot recall requests already sent, remove
Google cookies, or guarantee an already downloaded SDK stops processing.

## Activation and verification

Do not bootstrap Google or ads while publisher/site approval is missing.
Separately verify the real publisher, approved site, message and certified CMP,
privacy disclosures, vendor scope and root-host ads.txt requirements. Owner
authorization is required before external installation or public activation.
No current account access, certification or site acceptance is established here.

Run `node --test tests/google-cmp-provider.test.cjs tests/ads.test.cjs` for offline
protocol and loader mocks. They use synthetic data, not real user consent or ad
impressions. Live message accessibility, equal choices, keyboard/focus behavior,
blocking, withdrawal and network traces remain parent integration evidence.
Do not claim those checks from Node tests. Rollback: omit the local bridge and
retain disabled ads and consent readiness flags. No new runtime cost or library.

## Official references

Reviewed 15 October 2026. Recheck at activation because policy can change.

- [Google Funding Choices API](https://developers.google.com/funding-choices/fc-api-docs): readiness queue and revocation method.
- [Google publisher TCF integration](https://support.google.com/adsense/answer/9804260): Google legal bases and flexible-purpose restrictions.
- [IAB CMP API v2](https://github.com/InteractiveAdvertisingBureau/GDPR-Transparency-and-Consent-Framework/blob/master/TCFv2/IAB%20Tech%20Lab%20-%20CMP%20API%20v2.md): event lifecycle, listener removal, TCData and restriction types.

These references inform the adapter. They do not certify this code or authorize
account changes, deployment or advertising.

## Reviewed script delivery, CB-003

`web/google-cmp-boot.js` is the account-activation boundary. It requires the real published Google Privacy & messaging bootstrap script URL (`googleCMP.bootstrapScriptURL`), verified against the exact `ca-pub-` publisher ID, a reviewed Google message, current CMP ID/version, the approved origin and `/duo-casebook/` path. The public default is null, so no script is fetched. When approved, it queues Google's `CONSENT_API_READY` callback; only a real `__tcfapi` then exposes the provider to `ads-boot.js`. The ad controller waits for `casebook-cmp-ready`, then enforces its own consent and visibility checks. Missing or malformed approval fails closed and emits no ads.

The source URL pattern is not proof the snippet is the correct Google-approved European regulations message. Copy the exact code from the authenticated publisher account only after its site/message approval. Do not set the reviewed flags to force activation. Google may change its installation contract; re-check at the activation decision.

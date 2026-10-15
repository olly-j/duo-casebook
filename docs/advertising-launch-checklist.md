# CB-003 advertising launch checklist

Status: implementation and review guidance, not advertising approval or a published privacy declaration. Advertising stays off. This checklist supplements [advertising.md](advertising.md), [google-cmp.md](google-cmp.md) and [privacy-choices.md](privacy-choices.md); it does not replace project authority or owner gates.

Assessment: Lane C for activation. Outcome: an evidence-led path from the disabled scaffold to an explicitly authorised, consent-gated placement. Acceptance: current provider/account evidence, exact hosted files, real consent and refusal tests, accessible controls and owner authorisation. Non-goals: account creation, accepting terms, entering payment information, buying a domain, installing dependencies or activating ads in this task. The scanner itself has no runtime impact on visitors.

## Current position

Owner-supplied context, 15 October 2026: payments information is complete in onboarding; site connection is still required; the account's site entry is `olly-j.github.io`. This does not establish an active publisher account or site approval. The owner reports that the origin root returns 404 and has no ads.txt. Public research requests in this audit could not independently retrieve those two URLs, so that observation remains owner-reported. The local configuration has advertising disabled, null publisher/unit IDs and false approvals. No certified message deployment is established.

## Account and site evidence

- [ ] Owner checks the current account onboarding tasks and activation state. Record the date, exact status wording and a private evidence reference. Do not put account screenshots, payment details, legal identity or private correspondence in Git.
- [ ] Owner verifies the actual site entry, including the relationship between the origin and `/duo-casebook/`. Do not assume every github.io subdomain is eligible. Google notes that a site or subdomain can be ineligible in its [site-status guide](https://support.google.com/adsense/answer/12170222).
- [ ] Prefer the account-provided `google-adsense-account` meta tag in the document head for connection. It identifies the publisher without executing ad code. Copy the real public ID only with owner approval; validate its shape separately from its ownership. Do not use an unconditional ad SDK as a verification shortcut.
- [ ] Owner completes Verify and Request review in the site-connection flow. Google also offers ads.txt and script verification; availability must be confirmed in the actual account. See [Connect your site](https://support.google.com/adsense/answer/7584263).
- [ ] Record site status **Ready**, the date and exact site entry. **Getting ready** means checks are pending and can also reflect incomplete account tasks. **Needs attention** requires resolution. Payments completion, a valid-looking ID, a meta tag or a review request does not establish approval. Recheck the [status definitions](https://support.google.com/adsense/answer/12170222) before activation.
- [ ] Owner verifies no account or Policy centre restriction prevents serving, approves the real manual unit and host allowlist, and separately authorises this exact activation. Never infer consent from approval.

No review timing, acceptance, fill rate or income is promised.

## Root hosting and ads.txt decision

Google places ads.txt at the site's root, with the actual publisher declaration copied from the account. A project file at `/duo-casebook/ads.txt` does not serve `/ads.txt`. The record uses the `pub-` account form, whereas HTML configuration uses `ca-pub-`. Google describes ads.txt as recommended rather than universally mandatory; this project checklist conservatively requires the real root record before activation. See the [ads.txt guide](https://support.google.com/adsense/answer/12171612).

Implemented on 15 October 2026 in the separately authorised [public publisher-root repository](https://github.com/olly-j/olly-j.github.io). The independent CASEBOOK homepage, owner-publisher verification meta tag, links into the catalogue and privacy information, origin-root ads.txt and robots.txt were deployed. Public HTTPS returned HTTP 200 at both `/` and `/ads.txt`, and the exact public publisher declaration matched the approved format. This is hosting and crawler readiness only. Google AdSense approval remains unverified.

Ownership and continuing review responsibilities:

- A second public repository, publishing boundary and maintenance responsibility. The owner must approve creation, Pages settings and publication. The root page is part of the review surface; a thin landing page does not guarantee acceptance.
- Existing project paths must stay intact. Confirm canonical URLs, assets, crawler access and both Pages deployments after any change. Avoid an automatic redirect that removes the useful verification homepage.
- Root and project share an origin. Review localStorage keys, cookie scope and any service worker registration. A root worker could affect the project; none is proposed.
- A user site can affect the address of project sites if a custom domain is later added. Review GitHub's [user and project site model](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages) before changing it.
- No domain purchase is required by this proposal. Confirm current Pages eligibility and limits. A custom domain is a separate owner decision with registration/renewal costs, DNS control, HTTPS, canonical/consent scope changes and potentially another site review. Do not migrate solely on an assumption of easier AdSense acceptance.

After approved root publication, verify HTTPS 200 at `/` and `/ads.txt`, plain-text seller content, the exact authorised publisher record and no placeholder IDs. Check crawler access and the account's ads.txt status separately. A successful HTTP response is not proof Google has crawled or approved it.

## Certified message and three choices

Choose Google's actual Privacy & messaging European regulations message, or another currently Google-certified TCF CMP approved by the owner. Google's onboarding supports a three-button option. In Privacy & messaging, review the message for the actual site, privacy URL, language, vendors and purposes before publishing. Do not adopt account defaults without review. See [message editing](https://support.google.com/adsense/answer/10958856).

The first view must offer **Consent**, **Do not consent** and **Manage options**. Refusal must be as easy as acceptance: same view, comparable prominence, legible contrast and usable touch targets, without an extra refusal step. Check this in the real message on mobile, dark mode, zoom, keyboard and assistive technology. Avoid guilt, urgency or implying consent is required to browse. Keep a persistent, working Privacy choices entry point for withdrawal. A local informational dialog must hand off to the certified message; it cannot issue ad consent.

Verify the live CMP identity against Google's [certified CMP requirements/list](https://support.google.com/adsense/answer/13554116), the exact message/site pairing and adapter configuration. Certification is not a general finding of legal compliance. Confirm current TCF/GVL versions, Google vendor registration, legal bases, publisher restrictions and any Additional Consent dependencies. The current bridge supports a deliberately restricted Google-only consent route; see [its contract](google-cmp.md). Unknown geography, unavailable APIs, errors, malformed data, refusal and GPC must fail closed. No limited-ad or non-personalised fallback is approved here.

## Release and cookie/privacy evidence

Use fresh browser profiles and approved provider preview/test facilities first. Do not click live ads or create synthetic impressions. For any necessary final production observation, the owner must authorise it, keep it bounded and follow Google's [programme policies](https://support.google.com/adsense/answer/48182). Keep raw consent strings and request identifiers out of public evidence.

| Scenario | Required observation before activation |
| --- | --- |
| Disabled configuration | No Google CMP/ad SDK, ad preconnect, ad calls or optional advertising storage. Catalogue, sources and static privacy links work without JavaScript. |
| Approved CMP, before a choice | No ad request, ad SDK or ad storage. Distinguish necessary CMP transport/storage from advertising; document actual keys, purposes, scope and retention. |
| Do not consent | No ad request or optional ad storage, including reload and return visit. Browsing stays usable. |
| Manage options | Real purpose/vendor controls; saving refusal or an incomplete grant cannot enable ads. |
| Consent | Real CMP lifecycle and required legal bases precede the single eligible manual request. No request in comparison, saved-only, filter/dialog or excluded page states. |
| Withdrawal | Preferences open, denial propagates, pending SDK push is blocked, later navigation remains denied. Do not promise to recall sent requests, erase provider cookies or stop already downloaded code. |
| Missing, blocked, offline or malformed CMP | No ad request; no cached grant, fallback banner or fabricated success. |
| GPC and uncertain geography | No ad request under this project's conservative policy. |
| Storage denied or cleared | Safe denial/re-prompt as appropriate; no assumed consent and usable catalogue. |
| Navigation and accessibility | Verify focus return, Escape, touch, screen reader, 320px layout, zoom, light/dark, reduced motion and back-forward navigation. |

Record browser/device, region/test method, date, source revision, deployed revision, redacted network/storage observations and outcome for every row. Test rejection before acceptance in separate clean sessions. Compare cookies, localStorage and network requests before and after each action. Test the privacy page and footer from every page type. UI mocks and static scans do not prove these observations.

Update the actual privacy notice for providers, processing purposes, storage/retention, transfers where applicable and withdrawal behavior, based on the reviewed configuration. Preserve disclosure of hosting, saved cases and external gallery requests. Owner review of any privacy declaration remains required. Do not claim this checklist is legal advice or a compliance warranty.

## Read-only scanner

```sh
python3 -B scripts/adsense_readiness.py --site-url https://olly-j.github.io/duo-casebook/
python3 -B scripts/adsense_readiness.py --site-url https://olly-j.github.io/duo-casebook/ --remote --evidence /private/tmp/reviewed-ads-evidence.json
python3 -B -m unittest discover -s tests -p test_adsense_readiness.py
```

No network occurs without `--remote`. Remote mode makes bounded unauthenticated GETs to the supplied public HTTPS origin and project HTML/JS references in `docs/build-manifest.json`. It follows no redirects, sends no account credentials and executes no scripts. Responses are limited to 2 MB with a 10-second timeout per request. The operator supplies only a trusted public site URL; this is a local CLI, not an endpoint for untrusted URL submissions. Each manifest reference is fetched once, so large inventories can take time.

The scanner reads the literal source config without evaluating JavaScript, compares prepared config/source bytes and manifest SHA-256 hashes, flags direct ad scripts/resource hints, checks verification metadata, root availability and the real root seller record. All prepared HTML pages are conservatively checked for the same meta tag. It checks Google bridge configuration shape, not live CMP authenticity. Static inspection cannot discover every dynamic request or script behavior. Other provider implementations need an explicit scanner review rather than bypassing this check.

Optional evidence JSON contains owner-reviewed assertions, not credentials or proof authenticated by the scanner:

```json
{
  "publisherApproved": false,
  "siteApproved": false,
  "ownerActivationApproved": false,
  "privacyReviewed": false,
  "browserConsentTestsPassed": false,
  "cmp": {
    "certified": false,
    "id": null,
    "configId": null,
    "threeButtons": false,
    "adapterReviewed": false
  }
}
```

Set assertions only after the corresponding current evidence is reviewed. CMP ID must be a real positive IAB identifier, allowlisted by the reviewed bridge; configId must match the exact deployment. The scanner does not print publisher IDs, site URLs, account data or evidence content. Exit 1 means blocked or invalid input; exit 0 means `prerequisites_recorded`. `activation_authorized` is always false. Disabled ads are a safe state, not evidence of launch readiness.

Rebuild and run the final integrated Lane C gates through the parent before publication. Keep source-ready, deployed and publicly verified revisions separate. Recheck policies and provider versions at activation and after relevant configuration, vendor, domain or policy changes. No watcher is installed.

Rollback: keep advertising and consent readiness off; remove optional includes through the parent and deploy the last verified tree only with owner authority. A root-site rollback must preserve durable evidence and be separately reviewed. No request already transmitted can be recalled.

## External source review

Read-only review, 15 October 2026. Popularity and an open-source licence do not establish security or CMP certification. No repository was installed, imported or executed.

| Source | Appropriate use and decision |
| --- | --- |
| [IAB TCF specifications](https://github.com/InteractiveAdvertisingBureau/GDPR-Transparency-and-Consent-Framework) | Primary API/event and restriction reference. Standards inform implementation; they do not approve a publisher or turn an adapter into a certified CMP. Review the applicable current specification rather than legacy v1 material. |
| [IAB iabtcf-es](https://github.com/InteractiveAdvertisingBureau/iabtcf-es) | Official toolkit for TC strings, vendor lists, API and stubs, under Apache-2.0. Useful for independent validation research. A stub or encoder cannot establish that a real user consented. No runtime import is needed for this scanner. |
| [orestbida/cookieconsent](https://github.com/orestbida/cookieconsent) | Popular vanilla-JavaScript UI library, MIT licensed. Potential reference for preferences UI, but no Google certification was established by this review. Do not use its storage flags, category choices or Consent Mode integration as AdSense TCF authority. Avoid a competing second advertising banner. |
| [Google Android ad examples](https://github.com/googleads/googleads-mobile-android-examples) | Official mobile SDK examples, including a different platform's consent context. They do not implement this static website's consent contract. Do not port native UMP examples into the site. Use Google's web Privacy & messaging guidance and [Funding Choices API](https://developers.google.com/funding-choices/fc-api-docs) for the web bridge. |

Recommendation: retain the dependency-free local information controls and reviewed bridge, with Google's actual certified message as the consent source only after the owner completes provider setup. If any external code is later proposed, review its exact revision, licence, maintenance, transitive code and rollback separately. This review does not certify any repository as universally safe.

# CB-002 responsible publisher advertising

Status: source scaffold, OFF. This is AdSense publisher revenue, not a Google Ads buying campaign. No account, site, payment readiness or CMP approval is established by this code. Income and approval are not guaranteed.

## Contract and remaining gates

Lane C: new optional third-party processing. Outcome: one restrained manual responsive display placement only after approved configuration and certified consent. Non-goals: live activation, account creation, terms acceptance, payment entry, analytics, paid ranking, auto ads, anchors, vignettes, popups, refresh or synthetic impressions. No additional dependency or recurring service is installed. Potential CMP costs and privacy obligations need owner assessment before activation. Rollback: keep `enabled:false` and remove the loader include; revert these six source files if needed. Previously sent requests cannot be recalled by removing DOM.

The parent must independently verify the publisher account, obtain an explicitly approved public publisher ID and real manual ad-unit IDs, establish site approval and payment/tax readiness, approve a certified CMP and its configuration, update privacy disclosures, and secure owner authorization before enabling. Do not extract IDs from unrelated private data. Format checks cannot authenticate a publisher ID; they reject malformed and repeated-digit placeholders only. The checked-in config has `enabled:false`, null IDs, false approvals and an empty host allow-list. No Google script, preconnect, cookie, localStorage or CMP call is made by this module while disabled. An independently installed CMP has its own processing and must be assessed separately.

## Parent integration boundary

The parent owns HTML, page content, build copying and browser evidence. Include local `ads.css`, `ads-config.js`, then `ads.js`; those files do not self-start. Do not add a static Google snippet or Auto ads. Include no advertising metadata with a fabricated ID.

Create at most one empty `<aside hidden data-casebook-ad="catalogue"></aside>` after the complete catalogue, or use `article` after a substantive long guide. Never use thin case pages, privacy, 404, cards, filters, saved-only results, compare surfaces or dialogs. The parent must review each eligible guide for sufficient substantive content; there is no automatic word-count claim. Mark forbidden ancestors `data-ad-forbidden`. Keep the placement away from controls and footer links.

After loading the local files, call `CasebookAds.create(window, document, CASEBOOK_ADS_CONFIG).start({target, pageType, isEligible, consentProvider})`. `target` is the explicit empty aside; its immediately preceding element must be the completed content, whose bottom provides the offscreen measurement while the aside is hidden. Missing preceding content fails closed. `pageType` is only `catalogue` or `article`; `isEligible()` returns a strict boolean from the real current page/journey state. It must fail closed on missing state. Call controller `suppress()` when opening saved-only/compare/filter/dialog states or changing route; suppression is permanent for that controller/navigation. No reinsertion after revocation, error, no-fill or suppression. `destroy()` also unsubscribes and removes the script element, without promising to stop an already fetched SDK.

No privacy button is manufactured. Parent should link the actual privacy page. A “Privacy choices” button may be connected only to an installed CMP's documented, working open-preferences callback. Keep that callback separate from this ad loader; a button that does nothing is not a consent control.

## Certified consent provider: deliberately incomplete until separately implemented

This implementation chooses the explicitly permitted provider interface instead of claiming a complete TCF implementation. A bare `__tcfapi`, Consent Mode, localStorage boolean or hand-made banner is insufficient. No provider ships here. `consentReady` must remain false until the provider and server-approved/public deployment configuration are reviewed together. This static site has no server approval service; `consentConfigId` identifies the separately approved deployment configuration, not cryptographic proof or user authorization.

The provider implements `subscribe(callback)` and returns an unsubscribe function. It must subscribe to the real certified CMP's `__tcfapi('addEventListener', 2, callback)` lifecycle, propagate every update/error/withdrawal immediately, and never cache/replay a stale grant. While the CMP UI is open or state is uncertain, emit denial. Unsubscribe via the CMP's supported listener removal. The provider validates the current TC string, certified CMP identity/configuration, vendor disclosure, current vendor registration, publisher restrictions, relevant legal bases and any Additional Consent dependencies for the actual ad technology configuration. It emits `{authorized, fullLegalBases, configId, success, tcData}`. Both authorization fields may be true only after those full checks. They are attestation by the reviewed adapter, not sufficient proof by themselves. Do not wire arbitrary booleans to them.

The loader adds conservative guardrails: success true; loaded CMP; stable `tcloaded`/`useractioncomplete`; `gdprApplies===true`; nonempty TC string; vendor 755 consent; explicit consent for all configured purposes, with minimum [1,3,4,7,9,10]; present publisher restrictions map; each required purpose's vendor restriction absent or 1 (consent). Restriction 0 (not allowed), 2 (legitimate interest), malformed data, refusal, error or unknown denies. This intentionally demands consent even where Google may accept a different legal basis. The adapter must additionally evaluate the complete current legal-basis requirements; the guardrails alone are not consent completeness. No automatic allowance for non-EEA or uncertain geography. GPC true suppresses requests at admission, updates and delayed SDK load/push. The adapter must propagate privacy changes; the browser exposes no universal GPC change event.

## Rendering and failure behavior

After consent, reserve a fixed 340px shell before inserting the display unit. Reveal it only below the viewport; consent arriving when the placement is already in view produces no request on this navigation. Disabled/never-granted slots occupy no space. The standard async SDK URL, anonymous cross-origin attribute and standard manual responsive `ins` attributes are used. A single empty-object push occurs only after SDK load and actual visible geometry. One document may claim one slot, with one SDK load attempt and no retries or refresh timers.

No-fill and errors remove the ad DOM and make the shell invisible. Once reserved, space remains to avoid collapse shifting visible content. This tradeoff deliberately preserves a blank reservation after an attempted ad. Revocation before delayed load prevents push; revocation after push removes DOM and prevents new module requests. Removing an ad cannot recall previous network requests, erase Google's cookies or guarantee the downloaded SDK stops its internal processing. This is why live CMP/SDK withdrawal behavior requires separate approval and browser evidence before activation.

## Verification

`node --test --test-reporter=tap tests/ads.test.cjs` uses a VM and mock DOM/script/observer boundaries, with cookie/storage/timer traps. Fixture IDs never reach the network. It covers shipped disabled config, malformed IDs and gates, host/HTTPS checks, absent CMP, uncertain signals, purpose/vendor denials and restrictions, deferred load, visibility, duplicate signals, revoke before/after load, regrant, SDK/push/no-fill errors, GPC, eligibility, single placement and suppression. It does not prove live SDK behavior, CMP certification, accessibility, layout stability or account/site acceptance. Parent owns real-browser evidence with advertising disabled; do not exercise live ads for test impressions.

## ads.txt and hosting

Google's guidance requires ads.txt at the host root. For `https://olly-j.github.io/duo-casebook/`, that is **https://olly-j.github.io/ads.txt**, not `/duo-casebook/ads.txt`. This project cannot establish control of that root. Owner must resolve host-level control and use the real account-provided declaration before activation; no fake ads.txt is generated. A custom domain is optional and needs an owner decision, DNS/hosting control and renewed site approval assessment. Neither an ads.txt file nor embedding code alone establishes site approval.

## Official sources reviewed 15 October 2026

- [Google publisher consent requirements and certified CMP list](https://support.google.com/adsense/answer/13554116): Google-certified TCF CMP for relevant EEA/UK/Switzerland personalised inventory; certification is not full legal compliance.
- [Ad placement policies](https://support.google.com/adsense/answer/1346295): avoid accidental clicks and misleading placement; no refreshing, floating or popup placements here.
- [AdSense Program policies](https://support.google.com/adsense/answer/48182): no invalid impressions, owner clicks, click encouragement or deceptive advertising.
- [ads.txt guide](https://support.google.com/adsense/answer/12171612) and [legacy guide URL](https://support.google.com/adsense/answer/7532444) (redirects to the guide): real publisher declaration and root hosting.
- [Add a site and request review](https://support.google.com/adsense/answer/12169212): separate verification/review before serving.
- [Manage a CMP](https://support.google.com/adsense/answer/7670013) and [Google publisher TCF integration](https://support.google.com/adsense/answer/9804260): actual CMP configuration and legal-basis integration remain required.
- [IAB Tech Lab CMP API v2](https://github.com/InteractiveAdvertisingBureau/GDPR-Transparency-and-Consent-Framework/blob/master/TCFv2/IAB%20Tech%20Lab%20-%20CMP%20API%20v2.md): event listeners, TCData and publisher restriction semantics.

Policies and the certified list change. Recheck the applicable current requirements at the activation decision. These references grant no permission to activate, publish, accept terms or change project scope.

## Parent integration, CB-002

web/ads-boot.js now connects the guarded controller to explicit catalogue/article placements. It exits before work when advertising is disabled or a reviewed consent provider is absent. Public configuration retains null publisher/ad-unit IDs and false approvals. No live advertising was requested during tests. An existing AdSense account was located through owner-authorised account discovery; its current eligibility was not verified. Reactivation, site verification, real unit creation, certified CMP setup and root ads.txt placement remain external activation gates. Private account correspondence and publisher identifiers are not included in this public repository.

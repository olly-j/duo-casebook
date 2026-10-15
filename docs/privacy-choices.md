# CB-003 privacy controls

Status: integrated, tested privacy-control component ready for the CB-003 public release. Advertising remains disabled; no publisher consent or site approval is implied.

The footer Privacy choices control opens a native dialog. With optional advertising off it explains local saved cases, no analytics and no nonessential advertising requests. There is no accept-all banner because there are no optional cookies to accept in this configuration. No choice pre-authorises future partners.

Saved cases use the existing `casebook-saved` localStorage key. Clearing them requires a separate confirmation and removes only that key. It does not clear origin storage, cookies or advertising preferences. Open catalogue tabs must be reloaded because the current catalogue retains its own in-memory shortlist. Browser storage failure produces visible feedback. Nothing is persisted as advertising consent.

## Parent integration contract

Include `privacy-center.css` after shared styles and defer `privacy-center.js` after the catalogue application, on the catalogue and static reading pages. The module uses an existing footer `[data-ad-privacy]` button, or appends a button to the footer. It uses `/duo-casebook/privacy/` for the detailed page. Preserve that static link and all page content for visitors without JavaScript. If native dialog is unavailable, the module leaves the static link as the fallback.

The module claims the existing button's click in capture phase to prevent the older ads-boot handler from opening a second message. Parent should remove the older preference-button binding when integrating, leaving one owner for the control. Parent must ensure the ad loader observes this dialog before any optional ad activation. The control must remain usable even if catalogue data fails; load it after app.js, whose failure path disables existing buttons.

Advertising choices appears only with `CASEBOOK_ADS_CONFIG.enabled === true`, `consentReady === true` and a provider exposing `window.CASEBOOK_CONSENT_PROVIDER.openPreferences()`. Availability of this function is not evidence of certification. Parent owns certified-provider identity, configuration and runtime readiness validation. This module neither loads ads nor authorises requests. Missing providers fail closed in the separate advertising loader, and the dialog explains unavailability. Provider errors display recovery wording without inventing a consent result.

The local dialog closes before opening the provider. Accept, Decline, Manage, vendor disclosures, withdrawal and legally meaningful consent belong entirely to the real certified CMP message. Parent must verify that message's accessibility, current TCF integration and denial on errors before enabling advertising. No active CMP, complete publisher website verification or advertising approval is established by this work.

## Design and evidence

Native dialog supplies keyboard focus containment and inert background. Explicit Close and native Escape restore focus. Confirmation initially focuses Keep saved cases. Scoped styles use shared paper, ink, line and moss tokens, inherit dark mode, provide 44px controls, constrain width for 320px screens, and use no blur or motion. Browser and assistive-technology evidence remains an integration requirement; VM tests cannot prove layout or native browser behaviour.

Runtime dependencies, requests, cookies, timers and provider subscriptions added by this module: none. The only storage operation is user-confirmed removal of the existing shortlist key. `destroy()` removes owned DOM and listeners, ignores late promise failures, and supports later explicit `mount()`. No unload teardown is installed, preserving controls across back-forward cache restores.

## Guidance reviewed 15 October 2026

- [IAB Europe TCF supporting resources](https://iabeurope.eu/tcf-supporting-resources/) and [IAB Tech Lab TCF specifications](https://iabtechlab.com/standards/gdpr-transparency-and-consent-framework/) define the framework and CMP API. A local UI boolean is not a valid substitute for those signals.
- [ICO cookies and similar technologies guidance](https://ico.org.uk/for-organisations/direct-marketing-and-privacy-and-electronic-communications/guide-to-pecr/cookies-and-similar-technologies/) addresses device storage and consent. [ICO cookie-banner concerns](https://ico.org.uk/media2/migrated/4027811/cookie-banner-concerns.pdf) calls for equally prominent refusal where nonessential advertising cookies are offered. No such choices are fabricated in the disabled configuration.
- [Google certified CMP requirements](https://support.google.com/adsense/answer/13554020?hl=en-GB) require a certified TCF CMP for relevant publisher advertising. Certification does not alone establish legal compliance.
- [CookieConsent source and documentation](https://github.com/orestbida/cookieconsent) inform scoped styling, a small preference entry point and separation between UI and script activation. Self-hosting that open-source UI does not confer Google certification, establish a registered TCF CMP, disclose this site's actual vendors or create valid TC signals. It therefore cannot replace the required certified CMP. This implementation keeps zero runtime dependencies.

Lane B component within the parent's CB-003 release assessment. Acceptance: helpful disabled-mode information, isolated shortlist deletion, native dialog controls, provider delegation and error handling, no consent markers. Non-goals: CMP implementation, account verification, ad activation or publication. Rollback: remove the two source asset includes; static Privacy links remain. No recurring cost or external state changes.

## Integrated acceptance checks

The source component is now included on the catalogue and each static product, guide, method and privacy page. The real Chromium candidate exercises the native dialog at 320, 390 and 430 pixels in light and dark appearances, keyboard Escape, cancellation and confirmation of saved-list deletion, preservation of an unrelated localStorage key, and all static reading routes. The sampled axe privacy dialog check reported zero WCAG A/AA violations. With the disabled public configuration no Google CMP/AdSense calls were observed. These are local browser tests, not physical iOS or real approved-CMP consent tests.

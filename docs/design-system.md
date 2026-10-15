# CASEBOOK design system

CB-002, authored web interface. This document records design and copy decisions; product facts remain in research sources and generated catalogue data.

## Copy brief

| Field | Decision |
| --- | --- |
| Reader | UK-oriented iPhone Duo buyer, often browsing on a phone. |
| Prior knowledge | Knows the phone; may not know how case coverage or unpublished specifications differ. |
| Outcome | Find suitable cases, understand uncertainty, save, compare and check sources. |
| Literal ask | Compare iPhone Duo cases; use filters or choose priorities when useful. |
| Medium and budget | Responsive catalogue; hero under 30 words plus CTA, short action labels, expandable supporting evidence. |
| Register | Plain, specific and friendly. Source claims stay qualified. No unsupported testing claims or sales slogans. |

## Decisions

White is the default canvas. System sans typography uses tight display tracking, near-neutral body tracking and readable line heights. CASEBOOK retains its spaced wordmark. The new palette uses porcelain, graphite, neutral greys, and a blue focus ring. The short heading tells buyers what the site does. Photography, prices and coverage appear ahead of research detail.

Rounded controls have at least 44px targets; inputs use 16px text. Layouts use rem-based typography and flexible widths. At 360px and below, cards use one column. At intermediate phone widths, two columns keep photography early; browser evidence must confirm the layout at larger text sizes. Safe-area padding protects the header, sheets, footer and feedback.

Liquid Glass is reserved for navigation, filter controls, action capsules, and temporary sheets. Case photographs and factual content stay opaque. Solid colours remain the fallback. Reduced transparency and increased contrast remove blur. System dark mode changes canvas, surfaces, text and controls while retaining white source-image stages. Source photos are neither recoloured nor blended into the canvas. Forced-colour focus and control boundaries remain explicit.

Native dialogs and disclosures keep keyboard conventions. Save, compare, gallery navigation and filter changes provide direct state feedback without ornamental animation. Hover styling applies only to precise pointing devices. Reduced motion explicitly disables animation and transition effects. No motion library, font download, framework or dependency is added.

Case title anchors point to `cases/<id>/`. Photo buttons retain modal details. The detail view offers a canonical case-page link and product sharing. `?case=<id>` opens details while retaining filter parameters; it does not change document canonical metadata. Closing details removes that query selection. Product sharing uses the static URL without filter state.

The `#results` wrapper contains the `#products` grid and both static insertion markers, inside that grid. Build-time cards should replace only the region between markers. The runtime replaces grid contents only when catalogue data is available. If data.js is absent, static cards and anchors remain usable; interactive controls are disabled with visible recovery copy. The hidden advertisement slot follows the entire catalogue section. Its children belong to the ads module. Advertising does not affect catalogue order or preference matching.

“Not published” marks missing facts. Front-only, back-only and hinge coverage remain explicit. A manufacturer source is a source type, not a review score. Listed availability does not guarantee stock. Older-model reviews do not establish Duo performance. Prices retain source currencies. Supplied product summaries and source evidence remain factual content, not material for invented editorial claims.

## Selected references

The repository human-behaviour guidance informed familiar controls, grouped filters, readable target sizes and prompt feedback. These are design hypotheses; no usability study or task-completion improvement is claimed.

The selected local Apple, Emil design engineering and supplied writing guidance informed hierarchy, restraint, functional materials, short labels and answer-first copy. External initial-response instructions and animation suggestions do not override this task. Native SwiftUI API guidance is not used as a web API.

Official Apple reference routes: [typography](https://developer.apple.com/design/human-interface-guidelines/typography), [materials](https://developer.apple.com/design/human-interface-guidelines/materials), [accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility), [dark mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode), [motion](https://developer.apple.com/design/human-interface-guidelines/motion). The live pages returned JavaScript shells; the browsing tool could not retrieve their linked Markdown content. This is an Apple-inspired web interpretation, not a claim of certified platform conformance or verified iOS 27 specification compliance.

## Design and copy review

| Before | After | Why |
| --- | --- | --- |
| Large serif slogan and secondary editorial pitch | “Compare iPhone Duo cases” and a short useful introduction | Explain the task and bring search and photos earlier. |
| Warm paper canvas with repeated CSS overrides | One system of light/dark tokens and component rules | Make maintenance predictable and hierarchy consistent. |
| Small square controls | Rounded controls with 44px minimum targets and 16px inputs | Improve touch access and preserve legibility. |
| Modal-only product titles | Real static-page anchors plus photo-triggered details | Support crawling, new tabs and reliable product links. |
| Generic page sharing | Separate case sharing with a stable case URL | Let buyers share the exact product without unrelated filters. |
| Coverage separated from hinge facts | Front/back coverage and hinge status on each card | Help buyers distinguish complete protection from components. |
| Missing data replaced all cards with an empty state | Preserve static links and explain unavailable tools | Keep browsing useful during resource failure. |
| Generic footer slogan | Guide, method, privacy and gated privacy choices | Give buyers useful next steps and privacy access. |
| Editorial independence phrased as absence of monetisation | Ads do not affect case order; publisher ads labelled separately | Keep the claim compatible with separately governed advertising. |

## Evidence and limits

Focused VM tests cover case queries, filter preservation, static product sharing, missing-data recovery and integration boundaries. Existing UX tests cover gallery provenance and focus wiring. These checks do not substitute for browser layout, accessibility-tree, large-text, contrast, phone viewport or source-image evidence. The parent owns those integrated checks and publication gates.

Rollback: restore the three authored web files together. No product-data migration, external configuration or recurring cost is introduced.


## CB-005: Liquid Glass

Apple-style functional hierarchy separates the controls from the case content. The touch surfaces use regular, legible materials with fine edge highlights and restrained blur. Primary actions use graphite. Dark mode remains neutral.

The pinned, MIT-licensed liquidGL v3.0.0 renderer is lazy-loaded only for one compact desktop navigation dock on short pages. iPhone, long catalogue pages, reduced-motion or reduced-transparency users, and low-resource devices use the CSS material, with no optional GPU canvas. Resolution is 0.45 and tilt, fluid interaction, specular animation, and heavy shadow are disabled. Navigation, filters, browsing, and comparisons remain fully usable without the effect. Focus rings and native controls remain readable at increased contrast.

Source: Apple Human Interface Guidelines for materials and the provided naughtyduk/liquidGL source, pinned to blob b76e6872bf1c93ecacff646d09a77f5ce5f24ddb. Review the finished site in the full browser matrix and on a physical iPhone before treating the visual treatment as final.

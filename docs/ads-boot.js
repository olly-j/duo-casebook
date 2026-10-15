/* Optional CB-002 boundary. With the shipped disabled config, no listeners, storage or network are used. */
(function () {
  'use strict';
  const config = window.CASEBOOK_ADS_CONFIG;
  if (!config || config.enabled !== true || !window.CasebookAds) return;
  const provider = window.CASEBOOK_CONSENT_PROVIDER;
  if (!provider || typeof provider.subscribe !== 'function') return;
  const target = document.querySelector('[data-ad-placement]');
  if (!target) return;
  const pageType = target.dataset.adPlacement;
  if (!['catalogue', 'article'].includes(pageType)) return;
  target.dataset.casebookAd = pageType;
  const eligible = () => !document.querySelector('dialog[open]') &&
    (pageType === 'article' || document.documentElement.dataset.casebookView === 'browse');
  const controller = window.CasebookAds.create(window, document, config);
  if (!controller.start({target, pageType, isEligible: eligible, consentProvider: provider})) return;
  const observer = new MutationObserver(() => { if (!eligible()) controller.suppress(); });
  observer.observe(document.documentElement, {attributes:true, attributeFilter:['data-casebook-view']});
  document.querySelectorAll('dialog').forEach(dialog => observer.observe(dialog, {attributes:true,attributeFilter:['open']}));
  window.addEventListener('popstate', () => controller.suppress());
  window.addEventListener('pagehide', () => { observer.disconnect(); controller.destroy(); }, {once:true});
  if (typeof provider.openPreferences === 'function') {
    document.querySelectorAll('[data-ad-privacy]').forEach(button => {
      button.hidden = false;
      button.addEventListener('click', () => { controller.suppress(); provider.openPreferences(); });
    });
  }
})();

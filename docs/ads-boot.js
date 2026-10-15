/* CB-003: Start only when the reviewed CMP signals API readiness. */
(function () {
  'use strict';
  const config = window.CASEBOOK_ADS_CONFIG;
  if (!config || config.enabled !== true || !window.CasebookAds) return;
  let activated = false;
  function start() {
    if (activated) return;
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
    if (!controller.start({target, pageType, isEligible:eligible, consentProvider:provider})) return;
    activated = true;
    const observer = new MutationObserver(() => { if (!eligible()) controller.suppress(); });
    observer.observe(document.documentElement,{attributes:true,attributeFilter:['data-casebook-view']});
    document.querySelectorAll('dialog').forEach(d => observer.observe(d,{attributes:true,attributeFilter:['open']}));
    window.addEventListener('casebook-privacy-open',() => controller.suppress(),{once:true});
    window.addEventListener('popstate',() => controller.suppress());
    window.addEventListener('pagehide',() => {observer.disconnect();controller.destroy();},{once:true});
  }
  window.addEventListener('casebook-cmp-ready',start,{once:true});
  start();
})();

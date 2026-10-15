/* CB-003: certified Google CMP bootstrap. Inactive without independently reviewed approvals. */
(function () {
  'use strict';
  const c = window.CASEBOOK_ADS_CONFIG || {}, g = c.googleCMP || {};
  if (c.enabled !== true || c.publisherApproved !== true || c.siteApproved !== true ||
      c.consentReady !== true || g.reviewed !== true || g.certifiedConfigurationReviewed !== true ||
      g.legalBasesReviewed !== true || g.googleOnly !== true || g.additionalConsentRequired !== false ||
      !window.CasebookGoogleCMP || !Array.isArray(c.approvedHosts) ||
      !c.approvedHosts.includes(location.hostname) || location.protocol !== 'https:' ||
      g.approvedOrigin !== location.origin || g.approvedPath !== '/duo-casebook/' ||
      !location.pathname.startsWith(g.approvedPath) || g.configId !== c.consentConfigId ||
      g.publisherId !== c.publisherId || !Array.isArray(g.allowedCmpIds) || !g.allowedCmpIds.length || navigator.globalPrivacyControl === true) return;
  const source = g.bootstrapScriptURL;
  const id = typeof c.publisherId === 'string' ? c.publisherId : '';
  if (!/^ca-pub-[0-9]{16}$/.test(id) ||
      source !== 'https://fundingchoicesmessages.google.com/i/' + id.slice(3) + '?ers=1') return;
  const fc = window.googlefc = window.googlefc || {};
  fc.callbackQueue = fc.callbackQueue || [];
  const provider = window.CasebookGoogleCMP.create(window, document, c);
  fc.callbackQueue.push({ CONSENT_API_READY() {
    if (navigator.globalPrivacyControl === true || typeof window.__tcfapi !== 'function') return;
    window.CASEBOOK_CONSENT_PROVIDER = provider;
    window.dispatchEvent(new Event('casebook-cmp-ready'));
  }});
  const script = document.createElement('script');
  script.async = true; script.src = source; script.crossOrigin = 'anonymous';
  script.onerror = () => { window.CASEBOOK_CONSENT_PROVIDER = null; };
  document.head.appendChild(script);
})();

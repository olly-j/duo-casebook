/* CB-003. Local bridge only. Never installs a CMP or requests ads. */
(function (root) {
  'use strict';
  const BASE = [1, 2, 3, 4, 7, 9, 10];
  const FLEXIBLE = [2, 7, 9, 10];
  const map = value => value !== null && typeof value === 'object' && !Array.isArray(value);
  const positive = value => Number.isSafeInteger(value) && value > 0;
  function create(win, doc, config) {
    // Snapshot reviewed inputs. Later edits cannot activate this instance.
    const c = config || {}, r = c.googleCMP || {};
    const purposes = Array.isArray(c.requiredPurposes) ? c.requiredPurposes.slice() : [];
    const ids = Array.isArray(r.allowedCmpIds) ? r.allowedCmpIds.slice() : [];
    const configId = c.consentConfigId;
    const origin = r.approvedOrigin, path = r.approvedPath;
    const vendorListVersion = r.vendorListVersion, policyVersion = r.tcfPolicyVersion;
    const publisher = c.publisherId;
    const gated = c.enabled === true && c.publisherApproved === true && c.siteApproved === true &&
      c.consentReady === true && r.reviewed === true && r.certifiedConfigurationReviewed === true &&
      r.legalBasesReviewed === true && r.googleOnly === true && r.additionalConsentRequired === false &&
      r.publisherId === publisher && /^ca-pub-\d{16}$/.test(publisher || '') &&
      !/(\d)\1{15}$/.test((publisher || '').slice(7)) &&
      typeof configId === 'string' && configId.trim().length > 0 && r.configId === configId &&
      Array.isArray(c.approvedHosts) && c.approvedHosts.includes(win.location.hostname) &&
      typeof origin === 'string' && origin === win.location.origin && win.location.protocol === 'https:' &&
      path === '/duo-casebook/' && ids.length > 0 && ids.every(positive) &&
      positive(vendorListVersion) && positive(policyVersion) &&
      BASE.every(p => purposes.includes(p)) && purposes.every(p => positive(p) && p <= 10);
    const onSite = () => win.location.origin === origin &&
      win.location.protocol === 'https:' && win.location.pathname.startsWith(path);
    let ready = false;
    const denials = new Set();
    function external() {
      return gated && onSite() && win.googlefc && win.googlefc.callbackQueue &&
        typeof win.googlefc.callbackQueue.push === 'function' && typeof win.__tcfapi === 'function';
    }
    function allowed(t, success) {
      if (!external() || !ready || win.navigator?.globalPrivacyControl === true || success !== true || !map(t)) return false;
      if (t.cmpStatus !== 'loaded' || !['tcloaded', 'useractioncomplete'].includes(t.eventStatus) ||
          t.gdprApplies !== true || !ids.includes(t.cmpId) || !positive(t.listenerId) ||
          t.vendorListVersion !== vendorListVersion || t.tcfPolicyVersion !== policyVersion ||
          typeof t.tcString !== 'string' || !/^[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*$/.test(t.tcString) ||
          t.tcString.length < 20 || !map(t.vendor?.consents) || t.vendor.consents[755] !== true ||
          !map(t.purpose?.consents) || !map(t.publisher?.restrictions)) return false;
      return purposes.every(p => {
        if (t.purpose.consents[p] !== true) return false;
        const restrictions = t.publisher.restrictions;
        if (Object.hasOwn(restrictions, p) && !map(restrictions[p])) return false;
        const restriction = restrictions[p]?.[755];
        // Google defaults these flexible purposes to LI. Require the CMP to select consent.
        return FLEXIBLE.includes(p) ? restriction === 1 : restriction === undefined || restriction === 1;
      });
    }
    return Object.freeze({
      subscribe(fn) {
        if (typeof fn !== 'function') throw new TypeError('Consent callback required');
        let active = true, listenerId, removed = false;
        const api = win.__tcfapi;
        function emit(t, success) {
          let authorized = false, snapshot = null;
          try {
            snapshot = t == null ? null : JSON.parse(JSON.stringify(t));
            authorized = win.__tcfapi === api && allowed(snapshot, success);
          } catch (_) { snapshot = null; }
          // Each observer receives its own data, never a cached grant.
          try { fn({authorized, fullLegalBases: authorized, configId, success: success === true, tcData: snapshot}); } catch (_) { /* Observer isolation. */ }
        }
        function remove() {
          if (!removed && positive(listenerId) && typeof api === 'function') {
            removed = true;
            try { api.call(win, 'removeEventListener', 2, function () {}, listenerId); } catch (_) { /* Remain locally inactive. */ }
          }
        }
        const deny = () => { if (active) emit(null, false); };
        denials.add(deny);
        emit(null, false);
        if (external()) {
          try {
            win.googlefc.callbackQueue.push({CONSENT_API_READY: function () {
              if (!active || !external() || win.__tcfapi !== api) return;
              ready = true;
              try {
                api.call(win, 'addEventListener', 2, function (t, success) {
                  try {
                    if (positive(t?.listenerId)) listenerId = t.listenerId;
                  } catch (_) { if (active) emit(null, false); return; }
                  if (!active) { remove(); return; }
                  emit(t, success);
                });
              } catch (_) { emit(null, false); }
            }});
          } catch (_) { emit(null, false); }
        }
        return function () { active = false; denials.delete(deny); remove(); };
      },
      openPreferences() {
        if (!external() || !ready || typeof win.googlefc.showRevocationMessage !== 'function') return false;
        denials.forEach(deny => deny());
        try { win.googlefc.showRevocationMessage(); return true; } catch (_) { return false; }
      }
    });
  }
  root.CasebookGoogleCMP = Object.freeze({create});
})(typeof window === 'undefined' ? globalThis : window);

/* CB-002. Manual display only; no storage, CMP installation or automatic activation. */
(function (root) {
  'use strict';
  const claimedDocuments = new WeakSet();
  const BASE_PURPOSES = [1, 3, 4, 7, 9, 10];
  function createAds(win, doc, config) {
    const c = config || {};
    const host = win.location.hostname;
    const validId = value => typeof value === 'string' && /^ca-pub-\d{16}$/.test(value) && !/(\d)\1{15}$/.test(value.slice(7));
    const gated = c.enabled === true && c.publisherApproved === true && c.siteApproved === true &&
      c.consentReady === true && validId(c.publisherId) && typeof c.consentConfigId === 'string' &&
      c.consentConfigId.length > 0 && win.location.protocol === 'https:' &&
      Array.isArray(c.approvedHosts) && c.approvedHosts.includes(host) &&
      /^[a-z0-9.-]+\.[a-z]{2,}$/.test(host) &&
      !/(^|[.-])(localhost|local|test|dev|staging|example|invalid)([.-]|$)/i.test(host) &&
      Array.isArray(c.requiredPurposes) && BASE_PURPOSES.every(p => c.requiredPurposes.includes(p));
    let started = false, stopped = false, attempted = false, granted = false, pushed = false;
    let shell, unit, script, observer, visibilityObserver, unsubscribe;
    let eligible = () => false;
    const gpc = () => win.navigator.globalPrivacyControl === true;
    function hide() {
      if (unit) unit.remove();
      unit = null;
      if (shell) {
        // Keep the measured reservation once visible, avoiding a collapse-induced shift.
        shell.style.visibility = 'hidden';
        shell.setAttribute('aria-hidden', 'true');
      }
      if (observer) observer.disconnect();
      if (visibilityObserver) visibilityObserver.disconnect();
    }
    function deny() { granted = false; hide(); }
    function consentOK(s) {
      // The separately reviewed provider must validate *all* applicable legal bases,
      // vendor disclosures, TC string and restrictions, not merely these guardrails.
      try {
        const t = s.tcData;
        return s.authorized === true && s.fullLegalBases === true && s.configId === c.consentConfigId &&
          s.success === true && t.cmpStatus === 'loaded' &&
          ['tcloaded', 'useractioncomplete'].includes(t.eventStatus) && t.gdprApplies === true &&
          typeof t.tcString === 'string' && t.tcString.length > 0 && t.vendor.consents[755] === true &&
          t.publisher.restrictions && c.requiredPurposes.every(p =>
            t.purpose.consents[p] === true &&
            (t.publisher.restrictions[p]?.[755] === undefined || t.publisher.restrictions[p][755] === 1));
      } catch (_) { return false; }
    }
    function push() {
      if (pushed || !granted || stopped || gpc() || !eligible() || !unit || !unit.getClientRects().length) {
        if (gpc() || !eligible()) deny();
        return;
      }
      const r = unit.getBoundingClientRect();
      if (r.bottom <= 0 || r.top >= win.innerHeight || r.width <= 0) return;
      pushed = true;
      try { (win.adsbygoogle = win.adsbygoogle || []).push({}); } catch (_) { deny(); }
    }
    function request() {
      if (attempted || stopped || !granted || gpc() || !eligible()) return;
      // Reveal only below the viewport. Later consent requires a new navigation.
      const preceding = shell.previousElementSibling;
      if (!preceding || preceding.getBoundingClientRect().bottom < win.innerHeight) return;
      attempted = true;
      shell.hidden = false;
      shell.style.visibility = 'visible';
      shell.removeAttribute('aria-hidden');
      unit = doc.createElement('ins');
      unit.className = 'adsbygoogle';
      unit.style.display = 'block';
      unit.setAttribute('data-ad-client', c.publisherId);
      unit.setAttribute('data-ad-slot', c.slots[shell.dataset.casebookAd]);
      unit.setAttribute('data-ad-format', 'auto');
      unit.setAttribute('data-full-width-responsive', 'true');
      shell.appendChild(unit);
      observer = new win.MutationObserver(() => {
        if (unit && unit.getAttribute('data-ad-status') === 'unfilled') deny();
      });
      observer.observe(unit, { attributes: true, attributeFilter: ['data-ad-status'] });
      script = doc.createElement('script');
      script.async = true;
      script.src = 'https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=' + c.publisherId;
      script.crossOrigin = 'anonymous';
      script.onerror = deny;
      script.onload = () => {
        if (!granted || stopped || !unit || gpc() || !eligible()) { deny(); return; }
        visibilityObserver = new win.IntersectionObserver(push);
        visibilityObserver.observe(unit);
        push();
      };
      doc.head.appendChild(script);
    }
    return Object.freeze({
      start(options) {
        if (started || claimedDocuments.has(doc) || !gated || win.location.hostname !== host || win.location.protocol !== 'https:' || gpc()) return false;
        started = true;
        const o = options || {}, target = o.target, provider = o.consentProvider;
        if (!target || !['catalogue', 'article'].includes(o.pageType) ||
            target.dataset.casebookAd !== o.pageType || !/^\d{10}$/.test(c.slots?.[o.pageType] || '') ||
            /^(\d)\1{9}$/.test(c.slots[o.pageType]) ||
            target.closest('dialog,[role="dialog"],.card,[data-ad-forbidden]') ||
            typeof o.isEligible !== 'function' || !provider || typeof provider.subscribe !== 'function' ||
            typeof win.IntersectionObserver !== 'function' || typeof win.MutationObserver !== 'function') return false;
        eligible = () => { try { return o.isEligible() === true; } catch (_) { return false; } };
        if (!eligible()) return false;
        claimedDocuments.add(doc);
        shell = target;
        shell.hidden = true;
        shell.classList.add('casebook-ad');
        const label = doc.createElement('span');
        label.className = 'casebook-ad-label';
        label.textContent = 'Advertisement';
        shell.appendChild(label);
        try {
          unsubscribe = provider.subscribe(signal => {
            granted = !stopped && !gpc() && consentOK(signal);
            if (granted) request(); else deny();
          });
        } catch (_) { deny(); return false; }
        return true;
      },
      // Parent calls on saved-only/dialog/route changes; this can only suppress.
      suppress() { stopped = true; deny(); },
      destroy() {
        stopped = true; deny();
        if (typeof unsubscribe === 'function') unsubscribe();
        if (script) { script.onload = null; script.onerror = null; script.remove(); }
      }
    });
  }
  root.CasebookAds = Object.freeze({ create: createAds });
})(typeof window === 'undefined' ? globalThis : window);

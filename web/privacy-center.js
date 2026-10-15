/* CB-003. Local privacy controls, never an advertising consent implementation. */
(function () {
  'use strict';
  if (window.CasebookPrivacyCenter) return;
  let cleanup = null;
  function mount() {
    if (cleanup) return;
    const footer = document.querySelector('footer');
    if (!footer) return;
    const existing = footer.querySelector('[data-ad-privacy]');
    const trigger = existing || document.createElement('button');
    const original = existing && {text: trigger.textContent, hidden: trigger.hidden};
    trigger.type = 'button';
    trigger.textContent = 'Privacy & cookies';
    trigger.hidden = false;
    trigger.classList.add('privacy-center-trigger');
    if (!existing) footer.appendChild(trigger);
    const dialog = document.createElement('dialog');
    // Native dialog supplies modality, focus containment and inert background.
    if (typeof dialog.showModal !== 'function') {
      if (existing) { trigger.textContent = original.text; trigger.hidden = original.hidden; }
      else trigger.remove();
      return; // Keep the existing static Privacy link as the fallback.
    }
    dialog.className = 'privacy-center';
    dialog.setAttribute('aria-labelledby', 'privacy-center-title');
    dialog.innerHTML = '<h2 id="privacy-center-title">Your privacy</h2>' +
      '<p>Saved cases stay in this browser on this device. CASEBOOK does not use analytics.</p>' +
      '<p data-privacy-message></p><button type="button" data-privacy-ad hidden>Advertising choices</button>' +
      '<h3>Saved cases</h3><p>Clear your CASEBOOK favourites from this browser. Other site data stays as it is.</p>' +
      '<button type="button" data-privacy-clear>Clear saved cases…</button>' +
      '<div data-privacy-confirm hidden><p>Clear your saved cases? This cannot be undone. Reload open CASEBOOK tabs afterwards to update their lists.</p>' +
      '<button type="button" data-privacy-keep>Keep saved cases</button> <button type="button" data-privacy-delete>Yes, clear saved cases</button></div>' +
      '<p role="status" data-privacy-status></p><a href="/duo-casebook/privacy/">Read our privacy information</a>' +
      '<button type="button" data-privacy-close>Close</button>';
    document.body.appendChild(dialog);
    const find = selector => dialog.querySelector(selector);
    const message = find('[data-privacy-message]'), ad = find('[data-privacy-ad]');
    const confirm = find('[data-privacy-confirm]'), clear = find('[data-privacy-clear]');
    const status = find('[data-privacy-status]'), closeButton = find('[data-privacy-close]');
    let alive = true, returnTo = trigger;
    function provider() {
      const config = window.CASEBOOK_ADS_CONFIG;
      const candidate = window.CASEBOOK_CONSENT_PROVIDER;
      return config && config.enabled === true && config.consentReady === true && candidate &&
        typeof candidate.openPreferences === 'function' ? candidate : null;
    }
    function refresh() {
      const enabled = window.CASEBOOK_ADS_CONFIG?.enabled === true;
      ad.hidden = !provider();
      message.textContent = !enabled ? 'Optional advertising is off. No nonessential advertising requests are made. There are no optional cookies to accept, so we do not ask you to accept them or agree to future advertising partners.' :
        provider() ? 'Use Advertising choices to accept, decline or manage advertising in our consent provider’s message. CASEBOOK does not record advertising consent itself.' :
        'Advertising is unavailable because its consent controls are not ready. No advertising consent is assumed.';
    }
    function open(event) {
      // Own this button exclusively, including the older ads-boot click hook.
      event.preventDefault(); event.stopImmediatePropagation();
      if (dialog.open) return;
      refresh(); confirm.hidden = true; clear.hidden = false; status.textContent = '';
      returnTo = document.activeElement || trigger;
      dialog.showModal();
      if (typeof window.CustomEvent === "function") window.dispatchEvent(new window.CustomEvent("casebook-privacy-open"));
      closeButton.focus();
    }
    function restore() { if (returnTo?.isConnected) returnTo.focus(); }
    function close() { dialog.close(); }
    function cancel(event) { event.preventDefault(); close(); }
    function click(event) {
      const target = event.target;
      if (target === closeButton) close();
      if (target === clear) { confirm.hidden = false; clear.hidden = true; find('[data-privacy-keep]').focus(); }
      if (target === find('[data-privacy-keep]')) { confirm.hidden = true; clear.hidden = false; clear.focus(); }
      if (target === find('[data-privacy-delete]') && !confirm.hidden) {
        try {
          window.localStorage.removeItem('casebook-saved');
          status.textContent = 'Saved cases cleared. Reload open CASEBOOK tabs to update their lists.';
        } catch { status.textContent = 'Saved cases could not be cleared. Check your browser’s storage settings and try again.'; }
        confirm.hidden = true; clear.hidden = false; clear.focus();
      }
      if (target === ad) {
        const current = provider();
        if (!current) { refresh(); return; }
        // Close our modal before the certified CMP takes keyboard focus.
        close();
        try {
          Promise.resolve(current.openPreferences()).catch(failed);
        } catch { failed(); }
      }
    }
    function failed() {
      if (!alive) return;
      if (!dialog.open) dialog.showModal();
      message.textContent = 'Advertising choices could not open. Advertising consent has not been changed here. Please try again.';
      closeButton.focus();
    }
    trigger.addEventListener('click', open, true);
    dialog.addEventListener('click', click);
    dialog.addEventListener('cancel', cancel);
    dialog.addEventListener('close', restore);
    cleanup = () => {
      alive = false;
      if (dialog.open) close();
      trigger.removeEventListener('click', open, true);
      dialog.removeEventListener('click', click);
      dialog.removeEventListener('cancel', cancel);
      dialog.removeEventListener('close', restore);
      dialog.remove();
      if (existing) { trigger.textContent = original.text; trigger.hidden = original.hidden; trigger.classList.remove('privacy-center-trigger'); }
      else trigger.remove();
      cleanup = null;
    };
  }
  function destroy() { document.removeEventListener('DOMContentLoaded', mount); if (cleanup) cleanup(); }
  // Retain a mounted control across back-forward cache restores, without subscriptions.
  window.CasebookPrivacyCenter = {mount, destroy};
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once:true});
  else mount();
})();

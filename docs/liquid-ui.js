/* CB-005: optional liquidGL enhancement for a small, floating control.
   Native-looking CSS materials are the default on iPhone, Safari and long catalogues.
   Upstream: naughtyduk/liquidGL v3.0.0 (MIT), locally vendored and lazy loaded. */
(function () {
  'use strict';
  const tray = document.getElementById('compare-tray');
  const products = document.getElementById('products');
  if (!tray || !products || !window.matchMedia) return;

  const prefers = window.matchMedia('(min-width: 1100px) and (pointer: fine)');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const reduceTransparency = window.matchMedia('(prefers-reduced-transparency: reduce)');
  const moreContrast = window.matchMedia('(prefers-contrast: more)');
  let lens = null, loading = false, tried = false, scheduled = false, disposed = false;
  const safari = /Safari\//.test(navigator.userAgent) && !/(Chrome|Chromium|Edg|OPR)\//.test(navigator.userAgent);
  const touchDevice = /iPad|iPhone|iPod|Android/.test(navigator.userAgent);
  const limitedMemory = Number.isFinite(navigator.deviceMemory) && navigator.deviceMemory < 4;
  const limitedCPU = Number.isFinite(navigator.hardwareConcurrency) && navigator.hardwareConcurrency < 4;
  const dataSaver = !!navigator.connection?.saveData;

  function eligible() {
    return !disposed && document.visibilityState === 'visible' && !tray.hidden &&
      prefers.matches && !reduceMotion.matches && !reduceTransparency.matches && !moreContrast.matches && !safari && !touchDevice && !limitedMemory &&
      !limitedCPU && !dataSaver && !window.matchMedia('(forced-colors: active)').matches &&
      document.documentElement.scrollHeight <= 6400 &&
      products.querySelectorAll('.card').length > 0 &&
      products.querySelectorAll('.card').length <= 10 &&
      tray.getBoundingClientRect().width < window.innerWidth * .6;
  }

  function removeLens() {
    if (!lens) return;
    try { lens.destroy(); } catch (_) { /* CSS material remains available. */ }
    lens = null;
    tray.removeAttribute('data-glass-rendered');
  }

  function upgrade() {
    if (!eligible() || lens || loading || tried) return;
    tried = true; loading = true;
    const script = document.createElement('script');
    script.src = 'vendor/liquidGL.js';
    script.async = true;
    script.onload = () => {
      loading = false;
      if (!eligible() || typeof window.liquidGL !== 'function') return;
      try {
        lens = window.liquidGL({
          target: '#compare-tray', snapshot: 'body',
          engine: 'auto', resolution: 1,
          refraction: .006, aberration: 0,
          bevelWidth: .12, bevelDepth: .045, frost: 6,
          shadow: false, specular: false, tilt: false,
          reveal: 'none', interaction: 'none',
          draggable: false, magnify: 1, helper: false
        });
        if (lens && typeof lens.destroy === 'function') {
          tray.dataset.glassRendered = 'true';
        } else lens = null;
      } catch (_) {
        removeLens();
      }
    };
    script.onerror = () => { loading = false; };
    document.head.appendChild(script);
  }

  function schedule() {
    if (!eligible()) { removeLens(); return; }
    if (lens || loading || tried || scheduled) return;
    scheduled = true;
    const work = () => { scheduled = false; if (eligible()) upgrade(); };
    if (typeof window.requestIdleCallback === 'function') {
      window.requestIdleCallback(work, {timeout: 1800});
    } else setTimeout(work, 450);
  }

  const observer = new MutationObserver(schedule);
  observer.observe(tray, {attributes:true,attributeFilter:['hidden']});
  observer.observe(products, {childList:true});
  [prefers,reduceMotion,reduceTransparency,moreContrast].forEach(m => m.addEventListener?.('change',schedule));
  document.addEventListener('visibilitychange',schedule);
  window.addEventListener('pagehide',() => {
    disposed = true;
    observer.disconnect();
    [prefers,reduceMotion,reduceTransparency,moreContrast].forEach(m => m.removeEventListener?.('change',schedule));
    document.removeEventListener('visibilitychange',schedule);
    removeLens();
  }, {once:true});
  schedule();
})();

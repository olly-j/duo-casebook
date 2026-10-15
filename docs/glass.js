/* CASEBOOK CB-005. Optional progressive lens using MIT liquidGL v3.0.0.
 * Apple's functional materials stay in CSS on every phone. The GPU enhancement
 * is limited to a compact desktop navigation dock on short reading pages.
 * No input tracking, remote dependency, visual effects on product photography,
 * scroll listeners or animation loops are added by this loader. */
(() => {
  "use strict";
  const src = document.currentScript && document.currentScript.src;
  if (!src || !window.matchMedia) return;

  const required = "(min-width: 1024px) and (hover: hover) and (pointer: fine)";
  const blocked = [
    "(prefers-reduced-motion: reduce)",
    "(prefers-reduced-transparency: reduce)",
    "(prefers-contrast: more)",
    "(forced-colors: active)"
  ];
  const preference = window.matchMedia(required);
  const excluded = () => blocked.some(rule => window.matchMedia(rule).matches);
  const slowNetwork = () => {
    const c = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    return !!(c && (c.saveData || /(^2g$|slow-2g)/i.test(c.effectiveType || "")));
  };
  let effect = null;
  let requested = false;
  let disposed = false;
  const suitable = () => {
    if (!preference.matches || excluded() || slowNetwork()) return false;
    if (/(iPhone|iPad|iPod|Android)/i.test(navigator.userAgent || "")) return false;
    if (navigator.deviceMemory && navigator.deviceMemory < 6) return false;
    if (navigator.hardwareConcurrency && navigator.hardwareConcurrency < 8) return false;
    if (document.documentElement.scrollHeight > 3800) return false;
    if (!document.querySelector(".glass-dock")) return false;
    if (!window.WebGL2RenderingContext && !navigator.gpu) return false;
    if (new URL(location.href).searchParams.get("glass") === "off") return false;
    return !disposed && document.visibilityState === "visible";
  };

  function unload() {
    disposed = true;
    try { if (effect && typeof effect.destroy === "function") effect.destroy(); } catch (_) {}
    effect = null;
  }

  function enhance() {
    if (requested || !suitable()) return;
    requested = true;
    const script = document.createElement("script");
    script.async = true;
    script.src = new URL("vendor/liquidGL.js", src).href;
    script.onload = () => {
      if (!suitable() || typeof window.liquidGL !== "function") return;
      try {
        effect = window.liquidGL({
          target: ".glass-dock",
          snapshot: "body",
          engine: "auto",
          resolution: 0.45,
          refraction: 0.004,
          aberration: 0,
          frost: 1.5,
          bevelDepth: 0.04,
          bevelWidth: 0.1,
          shadow: false,
          specular: false,
          tilt: false,
          draggable: false,
          interaction: "none",
          reveal: "none",
          helper: false
        });
      } catch (_) { /* Native CSS material is the durable fallback. */ }
    };
    script.onerror = () => { requested = false; };
    document.head.appendChild(script);
  }

  function schedule() {
    if (!suitable()) return;
    const idle = window.requestIdleCallback;
    if (typeof idle === "function") {
      idle(() => { if (suitable()) enhance(); }, { timeout: 3000 });
    } else {
      window.setTimeout(() => { if (suitable()) enhance(); }, 1200);
    }
  }

  window.addEventListener("pagehide", unload, { once: true });
  if (document.readyState === "complete") schedule();
  else window.addEventListener("load", schedule, { once: true });
})();
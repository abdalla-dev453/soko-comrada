/**
 * Minimal analytics facade. Every call site in the app uses
 * trackPageView / trackEvent — swap the implementation here to wire
 * in Google Analytics (gtag.js) or Plausible without touching a
 * single component.
 *
 * To connect GA4: drop the gtag.js snippet in index.html, then
 * uncomment the window.gtag(...) calls below.
 *
 * To connect Plausible: add the Plausible script tag in index.html,
 * then uncomment the window.plausible(...) calls below.
 */

const isDev = import.meta.env.DEV;

export function trackPageView(path) {
  if (isDev) {
    console.debug("[analytics] page_view", path);
  }
  // window.gtag?.("event", "page_view", { page_path: path });
  // window.plausible?.("pageview", { u: window.location.origin + path });
}

export function trackEvent(name, props = {}) {
  if (isDev) {
    console.debug("[analytics] event", name, props);
  }
  // window.gtag?.("event", name, props);
  // window.plausible?.(name, { props });
}

/** Convenience wrapper for CTA buttons/links — keeps event names
 * consistent across the app (e.g. "cta_click:post_a_gig"). */
export function trackCtaClick(ctaId, extraProps = {}) {
  trackEvent(`cta_click:${ctaId}`, extraProps);
}
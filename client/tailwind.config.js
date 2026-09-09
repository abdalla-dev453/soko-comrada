/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // Semantic, CSS-variable-backed tokens so components never
        // hardcode a light/dark branch — see src/styles/index.css for
        // the :root / .dark variable definitions. rgb(... / <alpha>)
        // keeps Tailwind's opacity modifiers (bg-surface/60 etc) working.
        bg: "rgb(var(--color-bg) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        "surface-raised": "rgb(var(--color-surface-raised) / <alpha-value>)",
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        "ink-muted": "rgb(var(--color-ink-muted) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",

        // Fixed brand accents — same hue in both themes, only their
        // surrounding surfaces shift.
        marigold: {
          DEFAULT: "#E8A33D",
          strong: "#CE8A26",
          soft: "#FBEAD1",
        },
        coral: {
          DEFAULT: "#E8572F",
          strong: "#C6431F",
          soft: "#FCE0D6",
        },
        moss: {
          DEFAULT: "#4C7A5D",
          strong: "#3A6048",
          soft: "#DCEAE1",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "system-ui", "sans-serif"],
        body: ["'Work Sans'", "system-ui", "sans-serif"],
      },
      fontSize: {
        // Fluid type scale — clamp(min, preferred-vw, max) so headings
        // scale smoothly between a 360px phone and a desktop viewport
        // instead of jumping at breakpoints.
        "fluid-xs": ["clamp(0.78rem, 0.74rem + 0.2vw, 0.86rem)", { lineHeight: "1.5" }],
        "fluid-sm": ["clamp(0.88rem, 0.84rem + 0.2vw, 0.98rem)", { lineHeight: "1.55" }],
        "fluid-base": ["clamp(1rem, 0.96rem + 0.2vw, 1.08rem)", { lineHeight: "1.65" }],
        "fluid-lg": ["clamp(1.15rem, 1.08rem + 0.35vw, 1.35rem)", { lineHeight: "1.5" }],
        "fluid-xl": ["clamp(1.4rem, 1.25rem + 0.75vw, 1.85rem)", { lineHeight: "1.3" }],
        "fluid-2xl": ["clamp(1.9rem, 1.6rem + 1.5vw, 2.75rem)", { lineHeight: "1.15" }],
        "fluid-3xl": ["clamp(2.4rem, 1.9rem + 2.5vw, 4rem)", { lineHeight: "1.05" }],
        "fluid-hero": ["clamp(2.75rem, 2rem + 3.75vw, 5.5rem)", { lineHeight: "1.02" }],
      },
      borderRadius: {
        ticket: "0.5rem",
      },
      boxShadow: {
        card: "0 1px 2px rgb(0 0 0 / 0.04), 0 8px 24px -8px rgb(20 36 32 / 0.16)",
        "card-hover": "0 2px 4px rgb(0 0 0 / 0.06), 0 16px 32px -12px rgb(20 36 32 / 0.22)",
        popover: "0 4px 12px rgb(0 0 0 / 0.08), 0 24px 48px -16px rgb(20 36 32 / 0.28)",
      },
      backdropBlur: {
        nav: "14px",
      },
      keyframes: {
        "fade-in": {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        "rise-in": {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "toast-in": {
          "0%": { opacity: "0", transform: "translateY(8px) scale(0.98)" },
          "100%": { opacity: "1", transform: "translateY(0) scale(1)" },
        },
      },
      animation: {
        "fade-in": "fade-in 0.4s ease-out both",
        "rise-in": "rise-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) both",
        "toast-in": "toast-in 0.25s cubic-bezier(0.16, 1, 0.3, 1) both",
      },
      screens: {
        xs: "420px",
      },
    },
  },
  plugins: [],
};
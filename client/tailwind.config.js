export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Strict 60-30-10 editorial rule.
        // 60% = neutral slate / white backgrounds
        // 30% = dark slate text and surfaces
        // 10% = crisp indigo accent
        ink: "rgb(var(--color-ink) / <alpha-value>)",
        "ink-muted": "rgb(var(--color-ink-muted) / <alpha-value>)",
        "ink-faint": "rgb(var(--color-ink-faint) / <alpha-value>)",
        surface: "rgb(var(--color-surface) / <alpha-value>)",
        "surface-raised": "rgb(var(--color-surface-raised) / <alpha-value>)",
        border: "rgb(var(--color-border) / <alpha-value>)",
        accent: {
          DEFAULT: "rgb(var(--color-accent) / <alpha-value>)",
          strong: "rgb(var(--color-accent-strong) / <alpha-value>)",
          soft: "rgb(var(--color-accent-soft) / <alpha-value>)",
          muted: "rgb(var(--color-accent-muted) / <alpha-value>)",
        },
        // Semantic colors are kept minimal and flat — never neon, never multi-stop.
        success: {
          DEFAULT: "rgb(var(--color-success) / <alpha-value>)",
          soft: "rgb(var(--color-success-soft) / <alpha-value>)",
        },
        danger: {
          DEFAULT: "rgb(var(--color-danger) / <alpha-value>)",
          soft: "rgb(var(--color-danger-soft) / <alpha-value>)",
        },
        warning: {
          DEFAULT: "rgb(var(--color-warning) / <alpha-value>)",
          soft: "rgb(var(--color-warning-soft) / <alpha-value>)",
        },
      },
      fontFamily: {
        display: ["Fraunces", "serif"],
        sans: ["Source Sans 3", "system-ui", "sans-serif"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1.25" }],
        sm: ["0.875rem", { lineHeight: "1.4" }],
        base: ["1rem", { lineHeight: "1.55" }],
        lg: ["1.125rem", { lineHeight: "1.5" }],
        xl: ["1.5rem", { lineHeight: "1.35" }],
        "2xl": ["2rem", { lineHeight: "1.3" }],
        "3xl": ["2.5rem", { lineHeight: "1.25" }],
        "4xl": ["3rem", { lineHeight: "1.2" }],
      },
      spacing: {
        // 8px base grid — no arbitrary gaps
        4.5: "1.125rem",
        5.5: "1.375rem",
        6.5: "1.625rem",
        7.5: "1.875rem",
        18: "4.5rem",
      },
      borderRadius: {
        card: "0.75rem",
        button: "0.5rem",
      },
      boxShadow: {
        card: "0 1px 2px rgba(15, 23, 42, 0.06), 0 4px 16px rgba(15, 23, 42, 0.05)",
        "card-hover": "0 4px 12px rgba(15, 23, 42, 0.10), 0 16px 40px rgba(15, 23, 42, 0.08)",
        modal: "0 20px 40px rgba(15, 23, 42, 0.18)",
        popover: "0 4px 12px rgba(15, 23, 42, 0.08), 0 24px 48px -16px rgba(15, 23, 42, 0.20)",
        sticky: "0 -4px 16px rgba(15, 23, 42, 0.08)",
      },
      backdropBlur: {
        nav: "14px",
      },
      keyframes: {
        "soft-pulse": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "1" },
        },
      },
      animation: {
        "soft-pulse": "soft-pulse 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};
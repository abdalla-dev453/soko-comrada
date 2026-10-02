export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // CampusGig Kenya design system
        ink: "rgb(var(--brand-900) / <alpha-value>)",
        accent: "rgb(var(--brand-700) / <alpha-value>)",
        "accent-soft": "rgb(var(--brand-500) / <alpha-value>)",
        "on-brand": "rgb(var(--on-brand) / <alpha-value>)",
        "surface-raised": "rgb(var(--surface) / <alpha-value>)",
        "brand-900": "rgb(var(--brand-900) / <alpha-value>)",
        "brand-700": "rgb(var(--brand-700) / <alpha-value>)",
        "brand-500": "rgb(var(--brand-500) / <alpha-value>)",
        
        "success-100": "rgb(var(--success-100) / <alpha-value>)",
        "success-500": "rgb(var(--success-500) / <alpha-value>)",
        "success-700": "rgb(var(--success-700) / <alpha-value>)",
        
        "warning-100": "rgb(var(--warning-100) / <alpha-value>)",
        "warning-500": "rgb(var(--warning-500) / <alpha-value>)",
        "warning-700": "rgb(var(--warning-700) / <alpha-value>)",
        
        "danger-100": "rgb(var(--danger-100) / <alpha-value>)",
        "danger-500": "rgb(var(--danger-500) / <alpha-value>)",
        "danger-700": "rgb(var(--danger-700) / <alpha-value>)",
        
        surface: "rgb(var(--surface) / <alpha-value>)",
        canvas: "rgb(var(--canvas) / <alpha-value>)",
        "text-primary": "rgb(var(--text-primary) / <alpha-value>)",
        "text-secondary": "rgb(var(--text-secondary) / <alpha-value>)",
        border: "rgb(var(--border) / <alpha-value>)",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        xs: ["0.75rem", { lineHeight: "1.25" }],
        sm: ["0.875rem", { lineHeight: "1.4" }],
        base: ["1rem", { lineHeight: "1.55" }],
        lg: ["1.125rem", { lineHeight: "1.5" }],
        xl: ["1.5rem", { lineHeight: "1.35" }],
        "2xl": ["2rem", { lineHeight: "1.3" }],
        "3xl": ["2.5rem", { lineHeight: "1.25" }],
      },
      spacing: {
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
        card: "0 1px 2px rgba(11, 31, 58, 0.06), 0 4px 16px rgba(11, 31, 58, 0.05)",
        "card-hover": "0 4px 12px rgba(11, 31, 58, 0.10), 0 16px 40px rgba(11, 31, 58, 0.08)",
        modal: "0 20px 40px rgba(11, 31, 58, 0.18)",
        popover: "0 4px 12px rgba(11, 31, 58, 0.08), 0 24px 48px -16px rgba(11, 31, 58, 0.20)",
        sticky: "0 -4px 16px rgba(11, 31, 58, 0.08)",
      },
      backdropBlur: {
        nav: "14px",
      },
    },
  },
  plugins: [],
};

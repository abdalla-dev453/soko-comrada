import clsx from "clsx";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

import { pressable } from "../../utils/motion";

const VARIANT_CLASSES = {
  primary:
    "bg-accent text-ink hover:bg-accent-strong focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent/30",
  secondary:
    "bg-transparent border border-border text-ink hover:border-ink/30 hover:bg-surface-raised",
  ghost: "bg-transparent text-ink hover:bg-ink/5",
  danger: "bg-danger text-white hover:bg-danger/90",
};

const SIZE_CLASSES = {
  sm: "text-sm px-3.5 py-1.5 gap-1.5",
  md: "text-base px-5 py-2.5 gap-2",
  lg: "text-base px-6 py-3 gap-2.5",
};

export function Button({
  as: Component = "button",
  variant = "primary",
  size = "md",
  loading = false,
  disabled = false,
  fullWidth = false,
  icon: Icon,
  iconPosition = "left",
  className,
  children,
  ...props
}) {
  const isDisabled = disabled || loading;

  return (
    <motion.div
      variants={pressable}
      initial="rest"
      whileHover={isDisabled ? "rest" : "hover"}
      whileTap={isDisabled ? "rest" : "tap"}
      className={clsx(fullWidth && "w-full")}
    >
      <Component
        disabled={isDisabled}
        aria-busy={loading || undefined}
        className={clsx(
          "inline-flex items-center justify-center rounded-button font-medium",
          "transition-colors duration-150 focus-visible:outline-offset-2",
          "disabled:opacity-50 disabled:cursor-not-allowed",
          fullWidth && "w-full",
          VARIANT_CLASSES[variant],
          SIZE_CLASSES[size],
          className,
        )}
        {...props}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
        ) : (
          Icon &&
          iconPosition === "left" && (
            <Icon className="h-4 w-4" aria-hidden="true" />
          )
        )}
        <span>{children}</span>
        {!loading && Icon && iconPosition === "right" && (
          <Icon className="h-4 w-4" aria-hidden="true" />
        )}
      </Component>
    </motion.div>
  );
}
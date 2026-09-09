import clsx from "clsx";
import { motion } from "framer-motion";
import { Loader2 } from "lucide-react";

import { pressable } from "../../utils/motion";

const VARIANT_CLASSES = {
  primary:
    "bg-marigold text-[#4A1B0C] hover:bg-marigold-strong disabled:hover:bg-marigold shadow-card",
  secondary:
    "bg-transparent border border-ink/20 text-[#C9C9C4] hover:border-ink/40 hover:bg-ink/5",
  ghost: "bg-transparent text-ink hover:bg-ink/5",
  danger: "bg-marigold text-[#4A1B0C] hover:bg-marigold-strong",
};

const SIZE_CLASSES = {
  sm: "text-fluid-sm px-3.5 py-1.5 gap-1.5",
  md: "text-fluid-base px-5 py-2.5 gap-2",
  lg: "text-fluid-lg px-6 py-3.5 gap-2.5",
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
          "inline-flex items-center justify-center rounded-lg font-medium",
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

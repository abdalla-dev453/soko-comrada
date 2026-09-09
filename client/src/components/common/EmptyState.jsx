import { motion } from "framer-motion";

export function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col items-center text-center gap-3 py-16 px-6"
    >
      {Icon && (
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-moss-soft text-moss-strong mb-1">
          <Icon className="h-6 w-6" aria-hidden="true" />
        </div>
      )}
      <h3 className="text-fluid-lg font-display font-semibold">{title}</h3>
      {description && (
        <p className="text-fluid-sm text-ink-muted max-w-sm">{description}</p>
      )}
      {action && <div className="mt-2">{action}</div>}
    </motion.div>
  );
}
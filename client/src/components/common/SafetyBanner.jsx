import { Shield, AlertTriangle } from "lucide-react";

export function SafetyBanner({ className = "" }) {
  return (
    <div className={`safety-banner ${className}`}>
      <div className="flex items-start gap-2">
        <Shield className="h-5 w-5 text-brand-700 flex-shrink-0 mt-0.5" aria-hidden="true" />
        <div className="flex-1">
          <p className="font-semibold text-text-primary mb-0.5 flex items-center gap-1">
            <AlertTriangle className="h-4 w-4 text-warning-700" aria-hidden="true" />
            Never pay to apply. Report suspicious requests.
          </p>
          <p className="text-text-secondary text-sm">
            Legitimate employers on CampusGig Kenya never ask for money upfront.
            If anyone asks you to pay to apply or to move the conversation
            outside the platform, report them immediately.
          </p>
        </div>
      </div>
    </div>
  );
}

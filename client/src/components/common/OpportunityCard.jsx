import { MapPin, Clock, Star, ShieldCheck } from "lucide-react";
import { useMemo } from "react";
import { StatusChip } from "./StatusChip";
import { Button } from "./Button";

export function OpportunityCard({ opportunity, onApply, onSave, isSaved }) {
  const isClosingSoon = useMemo(() => {
    if (!opportunity.deadline) return false;
    const deadline = new Date(opportunity.deadline);
    const cutoff = new Date();
    cutoff.setTime(cutoff.getTime() + 48 * 60 * 60 * 1000);
    return deadline < cutoff;
  }, [opportunity.deadline]);

  return (
    <div className="card p-4 mb-4">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="text-subheading mb-1 line-clamp-1">{opportunity.title}</h3>
          <div className="flex items-center gap-2 mb-2">
            {opportunity.employer?.is_verified_employer && (
              <>
                <ShieldCheck className="h-4 w-4 text-success-700" aria-hidden="true" />
                <span className="badge badge-verified text-xs">Verified</span>
              </>
            )}
            {opportunity.employer && (
              <span className="text-text-secondary text-metadata">
                {opportunity.employer.business_name || opportunity.employer.name}
              </span>
            )}
          </div>
        </div>
        {onSave && (
          <Button
            variant="ghost"
            size="sm"
            icon={isSaved ? Star : Star}
            aria-label={isSaved ? "Unsave opportunity" : "Save opportunity"}
            onClick={() => onSave(opportunity)}
          />
        )}
      </div>

      <p className="text-body text-text-secondary mb-3 line-clamp-2">
        {opportunity.description}
      </p>

      <div className="grid grid-cols-2 gap-2 mb-3">
        {opportunity.compensation_type !== "UNPAID" && opportunity.budget && (
          <div className="flex items-center gap-1.5">
            <span className="text-text-primary font-semibold">
              KES {parseFloat(opportunity.budget).toLocaleString()}
            </span>
            <span className="text-text-secondary text-metadata">
              {opportunity.price_type === "FIXED" ? "fixed" : "from"}
            </span>
          </div>
        )}
        {opportunity.campus_location && (
          <div className="flex items-center gap-1.5 text-text-secondary">
            <MapPin className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <span className="text-metadata truncate">
              {opportunity.campus_location}
            </span>
          </div>
        )}
        {opportunity.landmark && (
          <div className="flex items-center gap-1.5 text-text-secondary">
            <MapPin className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <span className="text-metadata truncate">
              {opportunity.landmark}
            </span>
          </div>
        )}
        {opportunity.deadline && (
          <div className={`flex items-center gap-1.5 ${isClosingSoon ? "text-warning-700" : "text-text-secondary"}`}>
            <Clock className="h-4 w-4 flex-shrink-0" aria-hidden="true" />
            <span className="text-metadata">
              {new Date(opportunity.deadline).toLocaleDateString("en-GB", {
                day: "numeric",
                month: "short",
              })}
            </span>
          </div>
        )}
      </div>

      {opportunity.skills_required && opportunity.skills_required.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {opportunity.skills_required.slice(0, 3).map((skill) => (
            <span key={skill} className="badge bg-canvas text-text-secondary text-label">
              {skill}
            </span>
          ))}
          {opportunity.skills_required.length > 3 && (
            <span className="badge bg-canvas text-text-secondary text-label">
              +{opportunity.skills_required.length - 3} more
            </span>
          )}
        </div>
      )}

      {opportunity.is_featured && (
        <StatusChip status="PENDING_REVIEW" size="sm" />
      )}

      {onApply && (
        <Button
          variant="primary"
          fullWidth
          onClick={() => onApply(opportunity)}
          className="mt-3"
        >
          Apply now
        </Button>
      )}
    </div>
  );
}

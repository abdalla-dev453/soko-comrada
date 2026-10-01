import { Shield, Clock, Star } from "lucide-react";

export function TrustCard({ employer, onLearnMore }) {
  if (!employer) return null;

  const isVerified = employer.is_verified_employer;
  const rating = employer.avg_rating;
  const totalGigs = employer.total_gigs_posted || 0;

  return (
    <div className="trust-card">
      <h4 className="text-subheading mb-3 flex items-center gap-2">
        <Shield className="h-5 w-5 text-brand-700" aria-hidden="true" />
        Employer verification
      </h4>

      <div className="flex items-center gap-2 mb-3">
        {isVerified ? (
          <>
            <div className="flex items-center gap-1.5">
              <Shield className="h-5 w-5 text-success-700" aria-hidden="true" />
              <span className="font-semibold text-success-700">Verified</span>
            </div>
            <span className="text-text-secondary text-metadata">
              Business registration confirmed
            </span>
          </>
        ) : (
          <>
            <Clock className="h-5 w-5 text-warning-700" aria-hidden="true" />
            <span className="font-semibold text-warning-700">Under review</span>
          </>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="text-center">
          <div className="text-2xl font-bold text-text-primary">{totalGigs}</div>
          <div className="text-label text-text-secondary">Gigs posted</div>
        </div>
        {rating && (
          <div className="text-center">
            <div className="text-2xl font-bold text-text-primary flex items-center justify-center gap-1">
              <Star className="h-4 w-4 text-warning-700 fill-current" aria-hidden="true" />
              {rating}
            </div>
            <div className="text-label text-text-secondary">Rating</div>
          </div>
        )}
      </div>

      {onLearnMore && (
        <button
          onClick={onLearnMore}
          className="text-sm text-brand-700 font-semibold hover:underline"
        >
          How is this calculated?
        </button>
      )}
    </div>
  );
}

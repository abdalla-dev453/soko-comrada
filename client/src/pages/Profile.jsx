import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Star, ShieldCheck, MapPin } from "lucide-react";

import { SEO } from "../components/common/SEO";
import { SectionLoader } from "../components/common/Loader";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorBanner } from "../components/common/ErrorBanner";
import { fetchReviewsForUser } from "../api/gigs";

export default function Profile() {
  const { userId } = useParams();
  const [profile, setProfile] = useState(null);
  const [reviews, setReviews] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError("");
    fetchReviewsForUser(userId)
      .then((data) => {
        setProfile(data.user);
        setReviews(data.reviews);
      })
      .catch((err) => setError(err.message || "Couldn't load this profile."))
      .finally(() => setLoading(false));
  }, [userId]);

  if (loading) return <SectionLoader label="Loading profile…" />;

  return (
    <>
      <SEO
        title={profile ? profile.name : "Student profile"}
        description="Ratings and reviews from completed gigs."
        path={`/users/${userId}`}
        noindex
      />
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        {error && <ErrorBanner title="Couldn't load this profile" message={error} />}

        {profile && (
          <div className="mb-8">
            <div className="flex items-center gap-2">
              <ShieldCheck className="h-5 w-5 text-moss-strong" aria-hidden="true" />
              <h1 className="font-display font-semibold text-fluid-2xl">{profile.name}</h1>
              {profile.is_verified_entrepreneur && (
                <span className="rounded-full bg-marigold-soft px-2 py-0.5 text-fluid-xs font-medium text-marigold-strong">
                  Verified entrepreneur
                </span>
              )}
            </div>
            <div className="mt-2 flex items-center gap-4 text-fluid-sm text-ink-muted">
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" aria-hidden="true" />
                {profile.campus_location}
              </span>
              {profile.avg_rating != null && (
                <span className="inline-flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 fill-marigold text-marigold" aria-hidden="true" />
                  {profile.avg_rating.toFixed(1)}
                </span>
              )}
            </div>
            {profile.bio && <p className="mt-3 text-fluid-sm text-ink">{profile.bio}</p>}
          </div>
        )}

        <h2 className="font-display font-semibold text-fluid-lg mb-4">Reviews</h2>
        {reviews && reviews.length === 0 && (
          <EmptyState
            icon={Star}
            title="No reviews yet"
            description="Ratings appear here once gigs are completed."
          />
        )}
        {reviews && reviews.length > 0 && (
          <ul className="flex flex-col gap-3">
            {reviews.map((r) => (
              <li key={r.id} className="rounded-lg border border-border bg-surface p-4">
                <div className="flex items-center gap-1 mb-1.5">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-3.5 w-3.5 ${i < r.rating ? "fill-marigold text-marigold" : "text-border"}`}
                      aria-hidden="true"
                    />
                  ))}
                </div>
                {r.comment && <p className="text-fluid-sm text-ink">{r.comment}</p>}
                <p className="mt-1 text-fluid-xs text-ink-muted">
                  {new Date(r.created_at).toLocaleDateString("en-KE", { dateStyle: "medium" })}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}
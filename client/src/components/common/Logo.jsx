import { Briefcase } from "lucide-react";

export function Logo({ asLink = false }) {
  const mark = (
    <span className="inline-flex items-center gap-2 text-[1.35rem] font-semibold leading-none tracking-tight text-brand-900">
      <span className="grid size-9 shrink-0 place-items-center rounded-md bg-brand-700 text-white">
        <Briefcase className="h-5 w-5" aria-hidden="true" />
      </span>
      <span>CampusGig</span>
    </span>
  );

  return asLink ? (
    <a href="/" className="no-underline">{mark}</a>
  ) : mark;
}

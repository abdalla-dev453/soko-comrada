import { Link } from "react-router-dom";

export function Logo({ asLink = false }) {
  const mark = (
    <span className="group inline-flex items-center gap-2.5 text-[1.35rem] font-semibold leading-none tracking-tight text-ink">
      <span
        className="grid size-9 shrink-0 place-items-center rounded-md bg-accent text-white transition-transform duration-300 ease-out group-hover:-rotate-3"
      >
        <span className="text-[0.95rem] font-bold tracking-tighter">cp</span>
      </span>

      <span className="flex items-baseline">
        <span>Comrade</span>
        <span className="relative">
          Plug
          <span className="absolute inset-x-0 -bottom-0.5 h-[2px] bg-accent" />
        </span>
      </span>
    </span>
  );

  return asLink ? (
    <Link to="/" className="no-underline">
      {mark}
    </Link>
  ) : (
    mark
  );
}

import { Link } from "react-router-dom";

export function Logo({ asLink = false }) {
  const mark = (
    <span className="group inline-flex items-center gap-2.5 text-[1.35rem] font-semibold leading-none tracking-tight text-ink">
      <span
        className="relative grid size-9 shrink-0 place-items-center bg-marigold text-[#4A1B0C] transition-transform duration-300 ease-out group-hover:-rotate-3"
        style={{
          clipPath:
            "polygon(22% 0%, 100% 0%, 100% 78%, 78% 100%, 0% 100%, 0% 22%)",
        }}
      >
        <span className="text-[0.95rem] font-bold tracking-tighter">cp</span>
        <span
          className="absolute right-1 top-1 size-1 rounded-full"
          style={{ backgroundColor: "#D6FF3F" }}
        />
      </span>

      <span className="flex items-baseline">
        <span>Comrade</span>
        <span className="relative">
          Plug
          <span className="absolute inset-x-0 -bottom-0.5 h-[2px] bg-marigold" />
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

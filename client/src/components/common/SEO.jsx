import { Helmet } from "react-helmet-async";

const SITE_NAME = "Soko Comrada";
const SITE_URL = "https://sokocomrada.app";
const DEFAULT_IMAGE = `${SITE_URL}/og-default.png`;

/**
 * @param {{
 *   title: string,
 *   description: string,
 *   path?: string,          // e.g. "/about" — appended to SITE_URL
 *   image?: string,         // absolute URL, defaults to the site OG image
 *   noindex?: boolean,
 * }} props
 */
export function SEO({ title, description, path = "/", image = DEFAULT_IMAGE, noindex = false }) {
  const fullTitle = title.includes(SITE_NAME) ? title : `${title} · ${SITE_NAME}`;
  const url = `${SITE_URL}${path}`;

  return (
    <Helmet>
      <title>{fullTitle}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={url} />
      <meta name="robots" content={noindex ? "noindex, nofollow" : "index, follow"} />

      <meta property="og:type" content="website" />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={url} />
      <meta property="og:image" content={image} />
      <meta property="og:image:alt" content={`${SITE_NAME} — ${title}`} />

      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={image} />
    </Helmet>
  );
}
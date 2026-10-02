const frontendUrl = new URL(
  process.env.RENDER_FRONTEND_URL || "https://campusgig-kenya.onrender.com",
);
const apiUrl = new URL(
  process.env.RENDER_API_URL || "https://campusgig-kenya-api.onrender.com",
);
const checks = [];

async function check(name, url, validate, headers = {}) {
  try {
    const response = await fetch(url, {
      headers,
      signal: AbortSignal.timeout(20_000),
    });
    const result = await validate(response);
    if (!result.ok) throw new Error(result.message);
    checks.push({ name, ok: true });
    console.log(`PASS ${name}`);
  } catch (error) {
    checks.push({ name, ok: false });
    console.error(`FAIL ${name}: ${error.message}`);
  }
}

await check("frontend responds with the app shell", frontendUrl, async (response) => {
  const html = await response.text();
  return {
    ok:
      response.ok &&
      response.headers.get("content-type")?.includes("text/html") &&
      html.includes('id="root"') &&
      html.includes("CampusGig"),
    message: `HTTP ${response.status}; expected the CampusGig HTML app shell`,
  };
});

await check(
  "API health and database check",
  new URL("/api/health", apiUrl),
  async (response) => {
    const body = await response.json().catch(() => null);
    return {
      ok: response.ok && body?.status === "ok",
      message: `HTTP ${response.status}; received ${JSON.stringify(body)}`,
    };
  },
  { Origin: frontendUrl.origin },
);

await check("API permits the deployed frontend origin", new URL("/api/health", apiUrl), async (response) => ({
  ok: response.headers.get("access-control-allow-origin") === frontendUrl.origin,
  message: `Access-Control-Allow-Origin was ${response.headers.get("access-control-allow-origin") || "missing"}`,
}), { Origin: frontendUrl.origin });

for (const image of ["campus-gathering.jpg", "student-collaboration.jpg"]) {
  await check(`deployed image ${image}`, new URL(`/images/${image}`, frontendUrl), async (response) => ({
    ok: response.ok && response.headers.get("content-type")?.startsWith("image/"),
    message: `HTTP ${response.status}; expected an image response`,
  }));
}

if (checks.some((result) => !result.ok)) {
  console.error(`Render smoke check failed (${checks.filter((result) => !result.ok).length} check(s)).`);
  process.exitCode = 1;
} else {
  console.log("Render deployment smoke checks passed.");
}

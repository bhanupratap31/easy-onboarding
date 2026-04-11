import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND = process.env.BACKEND_URL ?? "http://localhost:8000";

// Headers that must not be forwarded upstream or back to the client
const HOP_BY_HOP = new Set([
  "host", "connection", "keep-alive", "transfer-encoding",
  "te", "trailer", "proxy-authorization", "proxy-authenticate",
  "upgrade", "content-encoding",
]);

async function proxy(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const url = `${BACKEND}/api/${path.join("/")}${req.nextUrl.search}`;

  const reqHeaders = new Headers();
  req.headers.forEach((v, k) => {
    if (!HOP_BY_HOP.has(k.toLowerCase())) reqHeaders.set(k, v);
  });

  let body: BodyInit | undefined;
  if (req.method !== "GET" && req.method !== "HEAD") {
    body = await req.text();
  }

  let upstream: Response;
  try {
    upstream = await fetch(url, {
      method: req.method,
      headers: reqHeaders,
      body,
    });
  } catch (e) {
    return new Response(JSON.stringify({ detail: `Backend unreachable: ${e}` }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  const resHeaders = new Headers();
  upstream.headers.forEach((v, k) => {
    if (!HOP_BY_HOP.has(k.toLowerCase())) resHeaders.set(k, v);
  });

  return new Response(upstream.body, {
    status: upstream.status,
    headers: resHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const DELETE = proxy;
export const PUT = proxy;
export const PATCH = proxy;

import { NextRequest } from "next/server";

export async function GET(request: NextRequest) {
  const url = request.nextUrl.searchParams.get("url");
  if (!url) {
    return Response.json({ error: "missing url" }, { status: 400 });
  }

  // Intentional fixture: attacker-controlled URL reaches server-side fetch.
  const response = await fetch(url);
  const body = await response.text();
  return new Response(body, { status: response.status });
}

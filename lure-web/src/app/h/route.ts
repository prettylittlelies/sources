export async function GET(request: Request) {
  const referer = request.headers.get('referer');

  if (!referer) {
    return Response.redirect("https://tempt.lol");
  }
  const res = await fetch("https://api.tempt.lol/health/history", {
    method: "GET",
    headers: {
      Authorization: "Bearer HarryAuthorizationBearer!@",
    },
    cache: "no-store"
  });

  const data = await res.json();
  return Response.json(data);
}

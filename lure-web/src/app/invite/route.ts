import { redirect } from "next/navigation";

export async function GET() {
  return redirect(
    "https://discord.com/oauth2/authorize?client_id=1367774588750266408",
  );
}

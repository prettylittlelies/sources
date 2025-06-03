import { Pool } from "pg";
import { AvatarHistoryDisplay } from "@/components/ui/avatar-history-display";

interface PageProps {
  params: Promise<{ userId: string }>;
  searchParams: Promise<{ [key: string]: string | undefined }>;
}

interface AvatarData {
  url: string;
  lastModified: string;
}

const isDev = process.env.NODE_ENV === "development" && !process.env.DATABASE_URL;
const ITEMS_PER_PAGE = 20;

const MOCK_DATA = {
  rows: [{
    username: "Development User",
    avatars: Array(25).fill({
      url: "https://s3.tempt.lol/avatarhistory/5e0ruPsYZEFMWgsQ.png",
      lastModified: new Date().toISOString(),
    }),
    totalCount: 25,
  }],
};

const pool = isDev ? null : new Pool({ connectionString: process.env.DATABASE_URL });

async function getLastModified(url: string): Promise<string> {
  try {
    const res = await fetch(url, { method: "HEAD" });
    return res.headers.get("last-modified") || "";
  } catch {
    return "";
  }
}

export async function generateMetadata({ params }: PageProps) {
  const { userId } = await params;
  
  let username = "User";
  if (!isDev && pool) {
    try {
      const result = await pool.query(`
        SELECT username FROM avh WHERE user_id = $1
      `, [userId]);
      if (result?.rows?.[0]) {
        username = result.rows[0].username;
      }
    } catch (error) {
      console.error("Error fetching username:", error);
    }
  } else {
    username = "Development User";
  }

  return {
    title: `${username}'s Avatar History • Tempt`,
    description: "View avatar history for Discord users.",
    themeColor: "#8faaa2",
    openGraph: {
      title: `${username}'s Avatar History • Tempt`,
      description: "View avatar history for Discord users.",
      url: `https://tempt.lol/avatarhistory/${userId}`,
      images: [
        {
          url: "https://s3.tempt.lol/min/av.png",
          width: 512,
          height: 512,
          alt: "Tempt Bot Logo",
        },
      ],
    },
    twitter: {
      card: "summary",
      title: `${username}'s Avatar History • Tempt`,
      description: "View avatar history for Discord users.",
      images: ["https://s3.tempt.lol/min/av.png"],
    },
  };
}

export default async function AvatarHistoryPage({ params, searchParams }: PageProps) {
  const [{ userId }, searchParamsResolved] = await Promise.all([
    params,
    searchParams
  ]);
  const page = Math.max(1, parseInt(searchParamsResolved.p ?? "1"));
  let initialData = null;

  if (isDev || !pool) {
    initialData = MOCK_DATA;
  } else {
    try {
      const countResult = await pool.query(`
        SELECT array_length(avatars, 1) as total_count
        FROM avh 
        WHERE user_id = $1
      `, [userId]);
      
      const totalCount = countResult.rows[0]?.total_count ?? 0;
      const offset = (page - 1) * ITEMS_PER_PAGE;
      
      const startIndex = Math.max(1, totalCount - offset - ITEMS_PER_PAGE + 1);
      const endIndex = totalCount - offset;
      
      const result = await pool.query(`
        WITH user_data AS (
          SELECT username, avatars
          FROM avh 
          WHERE user_id = $1
        )
        SELECT 
          username,
          ARRAY(
            SELECT unnest(avatars[$2:$3])
          ) as page_avatars
        FROM user_data
      `, [userId, startIndex, endIndex]);

      if (!result?.rows?.[0]) throw new Error("User not found");

      const avatarsWithDates = await Promise.all(
        (result.rows[0].page_avatars || []).map(async (url: string) => ({
          url,
          lastModified: await getLastModified(url),
        }))
      );

      avatarsWithDates.sort((a, b) => 
        new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
      );

      initialData = {
        rows: [{
          username: result.rows[0].username,
          avatars: avatarsWithDates,
          totalCount,
        }],
      };
    } catch (error) {
      console.error("Database error:", error);
      initialData = {
        rows: [{ username: null, avatars: [], totalCount: 0 }],
      };
    }
  }

  return (
    <main className="min-h-screen pt-24 pb-16 px-4">
      <div className="max-w-5xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-gradient mb-2">Avatar History</h1>
          <p className="text-muted-foreground">
            {initialData?.rows?.[0]?.username
              ? `View ${initialData.rows[0].username}'s previous Discord avatars`
              : "User not found"}
          </p>
        </div>
        <AvatarHistoryDisplay
          userId={userId}
          page={page}
          totalCount={initialData?.rows?.[0]?.totalCount ?? 0}
          initialAvatars={initialData?.rows?.[0]?.avatars || []}
          initialUsername={initialData?.rows?.[0]?.username}
        />
      </div>
    </main>
  );
}

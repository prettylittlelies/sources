interface PageProps {
  searchParams: Promise<{ [key: string]: string | undefined }>;
}

export default async function Connected({ searchParams }: PageProps) {
  const res = await searchParams;
  const username = res.username || "?";

  return (
    <main className="min-h-screen flex items-center justify-center pt-24 pb-16 px-4">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-medium text-gradient mb-2">
          Congratulations!
        </h1>
        <p className="text-gray-300/90 leading-relaxed">
          Your account (
          <a
            href={`https://last.fm/user/${username}`}
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium hover:underline transition-all duration-200 ease-in-out hover:opacity-80"
          >
            {username}
          </a>
          ) has been successfully linked to our system.
        </p>
      </div>
    </main>
  );
}

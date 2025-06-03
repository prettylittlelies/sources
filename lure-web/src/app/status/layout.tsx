export const metadata = {
  title: "Tempt • Status",
  description: "Check the current status and uptime of Tempt Bot.",
  openGraph: {
    title: "Tempt • Status",
    description: "Check the current status and uptime of Tempt Bot.",
    url: "https://tempt.lol/status",
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
    title: "Tempt • Status",
    description: "Check the current status and uptime of Tempt Bot.",
    images: ["https://s3.tempt.lol/min/av.png"],
  },
  themeColor: "#8faaa2",
};

export default function StatusLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

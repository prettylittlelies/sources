export const metadata = {
  title: "Tempt • Embed Builder",
  description:
    "Create and customize Discord embeds with our easy-to-use embed builder.",
  openGraph: {
    title: "Tempt • Embed Builder",
    description:
      "Create and customize Discord embeds with our easy-to-use embed builder.",
    url: "https://tempt.lol/embed",
    images: [
      {
        url: "https://s3.tempt.lol/min/av.png",
        width: 512,
        height: 512,
        alt: "Tempt Bot Logo",
      },
    ],
    themeColor: "#8faaa2",
  },
  twitter: {
    card: "summary",
    title: "Tempt • Embed Builder",
    description:
      "Create and customize Discord embeds with our easy-to-use embed builder.",
    images: ["https://s3.tempt.lol/min/av.png"],
  },
};

export default function EmbedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}

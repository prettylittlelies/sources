import "@/app/globals.css";
import "@radix-ui/themes/styles.css";
import { Inter } from "next/font/google";
import { MainNav } from "@/components/nav/MainNav";
import { Theme } from "@radix-ui/themes";
import { Toaster } from "sonner";
import { GradientContainer } from "@/components/ui/gradient-container";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata = {
  title: "Tempt",
  description:
    "An aesthetic, all-in-one bot that suits all your server's needs.",
  openGraph: {
    title: "Tempt Bot",
    description:
      "An aesthetic, all-in-one bot that suits all your server's needs.",
    url: "https://tempt.lol",
    images: [
      {
        url: "https://s3.tempt.lol/min/av.png",
        width: 512,
        height: 512,
        alt: "Tempt Bot Logo",
      },
    ],
    locale: "en_US",
    type: "website",
  },
  twitter: {
    card: "summary",
    title: "Tempt Bot",
    description:
      "An aesthetic, all-in-one bot that suits all your server's needs.",
    images: ["https://s3.tempt.lol/min/av.png"],
    themeColor: "#8faaa2",
  },
  icons: {
    icon: "https://s3.tempt.lol/min/av.png",
    shortcut: "https://s3.tempt.lol/min/av.png",
    apple: "https://s3.tempt.lol/min/av.png",
  },
  themeColor: "#8faaa2",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.className}>
      <body className="min-h-screen antialiased bg-[#406258b7]">
        <Theme
          appearance="dark"
          accentColor="jade"
          grayColor="slate"
          scaling="100%"
        >
          <GradientContainer />

          <div className="relative z-10">
            <MainNav />
            {children}
          </div>
          <Toaster
            theme="dark"
            position="top-right"
            richColors
            toastOptions={{
              style: {
                background: "rgba(17, 17, 17, 0.7)",
                backdropFilter: "blur(10px)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "#fff",
              },
              className: "glass-panel select-none",
            }}
          />
        </Theme>
      </body>
    </html>
  );
}

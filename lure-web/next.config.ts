import type { NextConfig } from "next";
import utwm from 'unplugin-tailwindcss-mangle';

const nextConfig: NextConfig = {
  reactStrictMode: false,
  poweredByHeader: false,
  compress: true,
  webpack: (config) => {
    config.plugins.push(utwm.webpack())
    return config
  },
  redirects: async () => {
    return [
      {
        source: "/embeds",
        destination: "/embed",
        permanent: false,
      },
    ];
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          {
            key: "X-Frame-Options",
            value: "DENY",
          },
          {
            key: "X-Content-Type-Options",
            value: "nosniff",
          },
          {
            key: "X-XSS-Protection",
            value: "1; mode=block",
          },
        ],
      },
    ];
  },
  images: {
    domains: [
      "cdn.discordapp.com",
      "media.discordapp.net",
      "i.imgur.com",
      "cdn.coffin.lol",
      "s3.tempt.lol",
      "s3.tempt.lol"
    ],
  },
};

export default nextConfig;

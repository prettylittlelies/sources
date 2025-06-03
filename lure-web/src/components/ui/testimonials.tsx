"use client";

import { Marquee } from "@/components/magicui/marquee";

interface User {
  id: string;
  username: string;
  avatar_url: string;
  bot: boolean;
}

interface TestimonialProps {
  testimonials: {
    userId: string;
    text: string;
    user: User;
  }[];
}

export function Testimonials({ testimonials }: TestimonialProps) {
  const halfLength = Math.ceil(testimonials.length / 2);
  const firstRow = testimonials.slice(0, halfLength);
  const secondRow = testimonials.slice(halfLength);

  return (
    <div className="relative flex flex-col w-full items-center overflow-hidden mask-fade gap-4">
      <Marquee className="py-6" pauseOnHover>
        {firstRow.map(({ user, text }, idx) => (
          <figure
            key={idx}
            className="relative max-w-[350px] mx-4 cursor-pointer overflow-hidden rounded-xl border p-3 transition-all duration-300 ease-out border-white/10 bg-background/50 backdrop-blur-sm hover:border-white/20 hover:bg-background/60"
          >
            <figcaption className="flex items-center gap-4 mb-4">
              <img
                src={user.avatar_url}
                alt={user.username}
                className="w-12 h-12 rounded-full ring-2 ring-white/10"
              />
              <div>
                <div className="font-medium text-muted-foreground">
                  @{user.username}
                </div>
              </div>
            </figcaption>
            <blockquote className="text-sm text-white/80 border-l-4 border-white/20 pl-3 text-left">
              {text}
            </blockquote>
          </figure>
        ))}
      </Marquee>
      <Marquee className="py-6" pauseOnHover reverse>
        {secondRow.map(({ user, text }, idx) => (
          <figure
            key={`second-${idx}`}
            className="relative max-w-[350px] mx-4 cursor-pointer overflow-hidden rounded-xl border p-3 transition-all duration-300 ease-out border-white/10 bg-background/50 backdrop-blur-sm hover:border-white/20 hover:bg-background/60"
          >
            <figcaption className="flex items-center gap-4 mb-4">
              <img
                src={user.avatar_url}
                alt={user.username}
                className="w-12 h-12 rounded-full ring-2 ring-white/10"
              />
              <div>
                <div className="font-medium text-muted-foreground">
                  @{user.username}
                </div>
              </div>
            </figcaption>
            <blockquote className="text-sm text-white/80 border-l-4 border-white/20 pl-3 text-left">
              {text}
            </blockquote>
          </figure>
        ))}
      </Marquee>
    </div>
  );
}

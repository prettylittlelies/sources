import { Box, Flex, Text } from "@radix-ui/themes";
import Marquee from "react-fast-marquee";

interface Guild {
  id: string;
  name: string;
  icon_url: string | null;
  member_count: number;
}

function GuildCard({ guild }: { guild: Guild }) {
  return (
    <div className="relative w-[300px] overflow-hidden rounded-xl border border-border/10">
      <div className="absolute inset-0 bg-gradient-to-br from-accent/5 via-transparent to-transparent"></div>
      <div className="relative p-4 backdrop-blur-sm transition-all hover:bg-accent/10">
        <div className="flex items-center gap-3">
          <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-xl bg-accent/5">
            <img
              src={guild.icon_url || `https://cdn.discordapp.com/embed/avatars/${parseInt(guild.id) % 6}.png`}
              alt={guild.name}
              className="h-full w-full object-cover"
            />
          </div>
          <div className="flex flex-col min-w-0 flex-1">
            <p className="text-sm font-bold text-primary truncate text-left leading-none">{guild.name}</p>
            <div className="flex items-center mt-1">
              <p className="text-xs text-muted-foreground text-left">
                {new Intl.NumberFormat("en-US", {
                  notation: "compact",
                  maximumFractionDigits: 1
                }).format(guild.member_count).toLowerCase()}
                <span className="ml-1"> members</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function FeaturedCommunities({ guilds }: { guilds: Guild[] }) {
  const filteredGuilds = guilds
    .filter(guild => guild.member_count >= 1000)
    .slice(0, 25);

  const firstRow = filteredGuilds.slice(0, Math.ceil(filteredGuilds.length / 2));
  const secondRow = filteredGuilds.slice(Math.ceil(filteredGuilds.length / 2));

  return (
    <div className="w-full overflow-hidden space-y-6">
      <Marquee
        speed={30}
        pauseOnHover
      >
        {firstRow.map((guild) => (
          <div className="mx-2" key={guild.id}>
            <GuildCard guild={guild} />
          </div>
        ))}
      </Marquee>

      <Marquee
        speed={30}
        direction="right"
        pauseOnHover
      >
        {secondRow.map((guild) => (
          <div className="mx-2" key={guild.id}>
            <GuildCard guild={guild} />
          </div>
        ))}
      </Marquee>
    </div>
  );
}
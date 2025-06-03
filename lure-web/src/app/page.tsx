import {
  Button,
  Container,
  Flex,
  Heading,
  Section,
  Text,
  Box,
} from "@radix-ui/themes";
import {
  SpeakerLoudIcon,
  LockClosedIcon,
  HeartIcon,
  Component2Icon,
  GearIcon,
  ChevronDownIcon,
} from "@radix-ui/react-icons";
import Link from "next/link";
import { Footer } from "@/components/ui/footer";
import { BentoCard, BentoGrid } from "@/components/magicui/bento-grid";
import { StatsCounter } from "@/components/ui/stats-counter";
import Image from "next/image";
import { FeaturedCommunities } from "@/components/ui/featured-communities";

const modCommands = [
  {
    name: "kick @user [reason]",
    body: "Kick a user from the server",
  },
  {
    name: "ban @user 7d [reason]",
    body: "Ban a user for 7 days with an optional reason",
  },
  {
    name: "mute @user 1h [reason]",
    body: "Mute a user for 1 hour with an optional reason",
  },
  {
    name: "clear 50",
    body: "Delete the last 50 messages in the current channel",
  },
  {
    name: "strip @user",
    body: "Remove all dangerous roles from a user",
  },
];

const lastFmStats = [
  {
    artist: "The Weeknd",
    plays: "2,547 plays",
    image: "https://i.scdn.co/image/ab67616d00001e02a048415db06a5b6fa7ec4e1a",
  },
  {
    artist: "Drake",
    plays: "1,892 plays",
    image: "https://i.scdn.co/image/ab67616d00001e02cd945b4e3de57edd28481a3f",
  },
  {
    artist: "Taylor Swift",
    plays: "1,563 plays",
    image: "https://i.scdn.co/image/ab67616d00001e02bb54dde68cd23e2a268ae0f5",
  },
];

const voiceSettings = [
  { name: "Limit", value: "4 users" },
  { name: "Bitrate", value: "256kbps" },
  { name: "Region", value: "US East" },
  { name: "Type", value: "Gaming" },
];

const configOptions = [
  { name: "Prefix", value: "," },
  { name: "Log Channel", value: "#mod-logs" },
  { name: "Welcome Message", value: "hi @user, welcome to Tempt" },
  { name: "Welcome Channel", value: "#welcome" },
  { name: "Auto Role", value: "@Member" },
];

const features = [
  {
    name: "Moderation",
    description:
      "Keep your server safe with powerful moderation tools and detailed logs.",
    Icon: LockClosedIcon,
    href: "/commands",
    cta: "View Commands",
    className: "col-span-3 lg:col-span-2",
    background: (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/5 via-transparent to-transparent" />
        <div className="absolute inset-x-0 top-8 grid grid-cols-2 gap-3 px-4 [mask-image:linear-gradient(to_top,transparent_40%,#000_100%)]">
          {modCommands.map((cmd, idx) => (
            <div
              key={idx}
              className="relative cursor-pointer overflow-hidden rounded-xl border border-[#8faaa2]/10 bg-[#8faaa2]/[0.02] p-3 transform-gpu blur-[0.2px] transition-all duration-300 ease-out hover:blur-none hover:bg-[#8faaa2]/[0.05] hover:scale-[1.02]"
            >
              <code className="text-sm font-mono text-[#8faaa2]/90 block mb-2">
                ,{cmd.name}
              </code>
              <p className="text-xs text-muted-foreground/80 line-clamp-2">
                {cmd.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    name: "LastFM Integration",
    description:
      "Track and share your music listening stats with your community.",
    Icon: HeartIcon,
    href: "/commands",
    cta: "View Commands",
    className: "col-span-3 lg:col-span-1",
    background: (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/5 via-transparent to-transparent" />
        <div className="absolute inset-x-0 top-8 flex flex-col gap-3 px-4 [mask-image:linear-gradient(to_top,transparent_30%,#000_100%)]">
          {lastFmStats.map((stat, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 p-2 rounded-lg border border-[#8faaa2]/10 bg-[#8faaa2]/[0.02] transform-gpu blur-[0.2px] transition-all duration-300 ease-out hover:blur-none hover:bg-[#8faaa2]/[0.05]"
            >
              <img
                src={stat.image}
                alt={stat.artist}
                className="w-10 h-10 rounded-md opacity-90"
              />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-[#8faaa2]/90 truncate">
                  {stat.artist}
                </div>
                <div className="text-xs text-muted-foreground/80">
                  {stat.plays}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    ),
  },
  {
    name: "VoiceMaster",
    description: "Create and manage dynamic voice channels with full control.",
    Icon: SpeakerLoudIcon,
    href: "/commands",
    cta: "View Commands",
    className: "col-span-3 lg:col-span-1",
    background: (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/5 via-transparent to-transparent" />
        <div className="absolute top-8 inset-x-0 px-4 [mask-image:linear-gradient(to_top,transparent_30%,#000_100%)]">
          <div className="p-3 rounded-lg border border-[#8faaa2]/10 bg-[#8faaa2]/[0.02] transform-gpu blur-[0.2px] transition-all duration-300 ease-out hover:blur-none hover:bg-[#8faaa2]/[0.05]">
            <div className="flex items-center justify-between mb-3">
              <div className="text-sm font-medium text-[#8faaa2]/90">
                compile's channel
              </div>
              <button className="p-1 rounded-md hover:bg-[#8faaa2]/10">
                <GearIcon
                  width="16"
                  height="16"
                  className="text-[#8faaa2]/70"
                />
              </button>
            </div>
            <div className="space-y-2">
              {voiceSettings.map((setting, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-center text-xs"
                >
                  <span className="text-muted-foreground/80">
                    {setting.name}
                  </span>
                  <span className="text-[#8faaa2]/80">{setting.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    ),
  },
  {
    name: "Configuration",
    description: "Customize the bot to perfectly fit your server's needs.",
    Icon: GearIcon,
    href: "/commands",
    cta: "View Commands",
    className: "col-span-3 lg:col-span-2",
    background: (
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/5 via-transparent to-transparent" />
        <div className="absolute top-8 inset-x-0 px-4 [mask-image:linear-gradient(to_top,transparent_30%,#000_100%)]">
          <div className="grid grid-cols-2 gap-3">
            {configOptions.map((option, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg border border-[#8faaa2]/10 bg-[#8faaa2]/[0.02] transform-gpu blur-[0.2px] transition-all duration-300 ease-out hover:blur-none hover:bg-[#8faaa2]/[0.05]"
              >
                <div className="text-xs font-medium text-muted-foreground/80 mb-1">
                  {option.name}
                </div>
                <div className="text-sm text-[#8faaa2]/90">{option.value}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
  },
];

interface TestimonialType {
  userId: string;
  text: string;
}

const testimonialData: TestimonialType[] = [
  {
    userId: "930383131863842816",
    text: "Love how Tempt handles our server! Easy to use with all needed features.",
  },
  {
    userId: "1273201960685928468",
    text: "Lure is a magical tool for every com server.",
  },
  {
    userId: "1323987827809058931",
    text: "Using Lure's user-app features for a while now, especially for the social media reposting stuff. Really love it.",
  },
];

async function getStats() {
  const res = await fetch("https://s3.tempt.lol/min/stats.json", {
    next: { revalidate: 60 },
  });
  const data = await res.json();

  const formatter = new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  });
  return {
    users: formatter.format(data.users).replace(".0", "").toLocaleLowerCase(),
    guilds: formatter.format(data.guilds).replace(".0", "").toLocaleLowerCase(),
  };
}

async function getGuilds() {
  const res = await fetch(`https://api.tempt.lol/discord/guilds`, {
    headers: {
      Authorization: `Bearer ${process.env.API_TOKEN}`,
    },
    next: { revalidate: 60 },
  });
  const guilds = await res.json();

  return guilds.filter((guild: { name: string; }) => {
    const lowerCaseName = guild.name.toLowerCase();
    const excludeKeywords = ['nsfw', 'boost', 'bot', 'dick', 'moved', 'join', 'shop', 's server', 'hate', 'gateway'];
    return !excludeKeywords.some(keyword => lowerCaseName.includes(keyword));
  });
}

export default async function Home() {
  const [{ users, guilds }, guildsData] = await Promise.all([
    getStats(),
    getGuilds(),
  ]);

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <main className="relative">
        <Section className="min-h-screen flex items-center justify-center relative py-16 sm:py-0">
          <Container className="w-full">
            <Flex
              direction="column"
              align="center"
              gap="4"
              className="max-w-[600px] w-full mx-auto px-4 sm:px-0"
            >
              <div className="text-center space-y-2 w-full">
                <Image
                  src="https://s3.tempt.lol/min/av.png"
                  alt="Bot Avatar"
                  width={96}
                  height={96}
                  className="rounded-full mx-auto"
                  unoptimized
                />
                <Heading
                  size={{ initial: "7", sm: "8" }}
                  className="text-gradient leading-[1.1] tracking-tight font-bold"
                >
                  A powerful Discord bot for your community
                </Heading>
                <StatsCounter users={users} guilds={guilds} />
              </div>
              <Flex gap="4" wrap="wrap" justify="center" className="w-full">
                <Button
                  size={{ initial: "3", sm: "4" }}
                  style={{
                    backgroundColor: "#8faaa2",
                    color: "#1a1a1a",
                    border: "none"
                  }}
                  asChild
                >
                  <Link href="/invite" className="flex items-center gap-2">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09-.01-.02-.04-.03-.07-.03-1.5.26-2.93.71-4.27 1.33-.01 0-.02.01-.03.02-2.72 4.07-3.47 8.03-3.1 11.95 0 .02.01.04.03.05 1.8 1.32 3.53 2.12 5.24 2.65.03.01.06 0 .07-.02.4-.55.76-1.13 1.07-1.75.02-.04 0-.08-.04-.09-.57-.22-1.11-.48-1.64-.78-.04-.02-.04-.08-.01-.11.11-.08.22-.17.33-.25.02-.02.05-.02.07-.01 3.44 1.57 7.15 1.57 10.55 0 .02-.01.05-.01.07.01.11.09.22.17.33.26.04.03.04.09-.01.11-.52.31-1.07.56-1.64.78-.04.01-.05.06-.04.09.32.61.68 1.2 1.07 1.75.03.02.06.03.09.01 1.72-.53 3.45-1.33 5.25-2.65.02-.01.03-.03.03-.05.44-4.53-.73-8.46-3.1-11.95-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.83 2.12-1.89 2.12z"
                        fill="currentColor"
                      />
                    </svg>
                    Add to Discord
                  </Link>
                </Button>
                <Button
                  size={{ initial: "3", sm: "4" }}
                  style={{
                    backgroundColor: "rgba(143, 170, 162, 0.1)",
                    color: "#a5c0b7",
                    backdropFilter: "blur(20px)",
                    border: "1px solid rgba(143, 170, 162, 0.3)"
                  }}
                  asChild
                >
                  <Link href="/commands" className="flex items-center gap-2">
                    <Component2Icon width="20" height="20" />
                    View Commands
                  </Link>
                </Button>
              </Flex>
            </Flex>
          </Container>

          <div className="absolute bottom-12 left-1/2 -translate-x-1/2">
            <Box className="animate-bounce">
              <ChevronDownIcon
                width="24"
                height="24"
                className="text-muted-foreground"
              />
            </Box>
          </div>
        </Section>

        <Section
          size="3"
          className="border-t border-border/20 bg-background/30 backdrop-blur-md"
        >
          <Container className="px-4 sm:px-6">
            <BentoGrid className="max-w-6xl mx-auto">
              {features.map((feature, idx) => (
                <BentoCard key={idx} {...feature} />
              ))}
            </BentoGrid>
          </Container>
        </Section>

        <Section
          size="3"
          className="border-t border-border/20 bg-background/20 backdrop-blur-md"
        >
          <Container>
            <Flex
              direction="column"
              align="center"
              gap="6"
              className="max-w-[800px] mx-auto px-4 sm:px-6 text-center"
            >
              <div className="space-y-3">
                <Heading size="8" className="text-gradient mb-2">
                  Featured Communities
                </Heading>
                <Text size="4" className="text-muted-foreground/80">
                  Join these thriving communities powered by Tempt
                </Text>
              </div>
              <div className="w-full">
                <FeaturedCommunities guilds={guildsData} />
              </div>
            </Flex>
          </Container>
        </Section>

        <Section size="3" className="border-t border-border/20">
          <Container>
            <Flex
              direction="column"
              align="center"
              gap="6"
              className="max-w-[600px] mx-auto px-4 sm:px-6 text-center"
            >
              <Heading size="8" className="text-gradient">
                Ready to get started?
              </Heading>
              <Text as="p" size="4" color="gray">
                Join thousands of communities already using Tempt to manage and
                enhance their Discord servers.
              </Text>
              <Button
                size={{ initial: "3", sm: "4" }}
                style={{
                  backgroundColor: "#8faaa2",
                  color: "#1a1a1a",
                  border: "none"
                }}
                asChild
              >
                <Link href="/invite" className="flex items-center gap-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                    <path
                      d="M19.27 5.33C17.94 4.71 16.5 4.26 15 4a.09.09 0 0 0-.07.03c-.18.33-.39.76-.53 1.09a16.09 16.09 0 0 0-4.8 0c-.14-.34-.35-.76-.54-1.09-.01-.02-.04-.03-.07-.03-1.5.26-2.93.71-4.27 1.33-.01 0-.02.01-.03.02-2.72 4.07-3.47 8.03-3.1 11.95 0 .02.01.04.03.05 1.8 1.32 3.53 2.12 5.24 2.65.03.01.06 0 .07-.02.4-.55.76-1.13 1.07-1.75.02-.04 0-.08-.04-.09-.57-.22-1.11-.48-1.64-.78-.04-.02-.04-.08-.01-.11.11-.08.22-.17.33-.25.02-.02.05-.02.07-.01 3.44 1.57 7.15 1.57 10.55 0 .02-.01.05-.01.07.01.11.09.22.17.33.26.04.03.04.09-.01.11-.52.31-1.07.56-1.64.78-.04.01-.05.06-.04.09.32.61.68 1.2 1.07 1.75.03.02.06.03.09.01 1.72-.53 3.45-1.33 5.25-2.65.02-.01.03-.03.03-.05.44-4.53-.73-8.46-3.1-11.95-.01-.01-.02-.02-.04-.02zM8.52 14.91c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.84 2.12-1.89 2.12zm6.97 0c-1.03 0-1.89-.95-1.89-2.12s.84-2.12 1.89-2.12c1.06 0 1.9.96 1.89 2.12 0 1.17-.83 2.12-1.89 2.12z"
                      fill="currentColor"
                    />
                  </svg>
                  Add to Discord
                </Link>
              </Button>
            </Flex>
          </Container>
        </Section>
        <Footer />
      </main>
    </div>
  );
}

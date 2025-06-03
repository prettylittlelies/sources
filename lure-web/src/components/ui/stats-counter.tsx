"use client";

import CountUp from "react-countup";
import { useInView } from "react-intersection-observer";

interface StatsCounterProps {
  users: string;
  guilds: string;
}

export function StatsCounter({ users, guilds }: StatsCounterProps) {
  const { ref, inView } = useInView({
    threshold: 0.2,
    triggerOnce: true,
  });

  const parseValue = (str: string) => {
    const num = parseFloat(str.replace(/[^0-9.]/g, ""));
    const suffix = str.replace(/[0-9.]/g, "");
    return { num, suffix };
  };

  const userStats = parseValue(users);
  const guildStats = parseValue(guilds);

  return (
    <p ref={ref} className="text-muted-foreground">
      serving{" "}
      {inView ? (
        <CountUp
          className="text-primary"
          end={userStats.num}
          separator=","
          decimals={userStats.num % 1 !== 0 ? 1 : 0}
          duration={2}
          suffix={userStats.suffix}
        />
      ) : (
        "0"
      )}{" "}
      users across{" "}
      {inView ? (
        <CountUp
          className="text-primary"
          end={guildStats.num}
          separator=","
          decimals={guildStats.num % 1 !== 0 ? 1 : 0}
          duration={2}
          suffix={guildStats.suffix}
        />
      ) : (
        "0"
      )}{" "}
      guilds
    </p>
  );
}

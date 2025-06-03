"use client";

import React, { useState, useEffect } from "react";
import { HiClock } from "react-icons/hi";
import { HiCube, HiServerStack, HiSignal, HiUsers, HiWifi } from "react-icons/hi2";
import { AnalyticsGraph } from "@/components/AnalyticsGraph";
import { formatDistanceToNow } from "date-fns";

interface ShardStats {
  id: number;
  guilds: number;
  users: number;
  channels: number;
  latency: number;
}

interface BotStats {
  timestamp: string;
  guilds: number;
  users: number;
  channels: number;
  shards: number;
  latency: number;
  uptime: string;
  commands_used: number;
  shard_stats: { [key: string]: ShardStats };
}

interface HistoryData {
  history: {
    guild_count: number;
    total_members: number;
    status: string;
    timestamp: string;
  }[];
}

function StatCard({
  label,
  value,
  className = "",
}: {
  label: string;
  value: string;
  className?: string;
}) {
  return (
    <div className={`glass-panel backdrop-blur-sm bg-background/50 p-4 ${className}`}>
      <div className="text-sm text-white/60 mb-1 font-medium">{label}</div>
      <div className="text-lg font-medium">{value}</div>
    </div>
  );
}

export default function StatusPage() {
  const [stats, setStats] = useState<BotStats | null>(null);
  const [history, setHistory] = useState<HistoryData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [statsRes, healthRes] = await Promise.all([
          fetch("/s", { priority: "high", cache: "no-store" }),
          fetch("/h", { priority: "high", cache: "no-store" })
        ]);

        if (!statsRes.ok || !healthRes.ok) {
          throw new Error("API request failed");
        }

        const [statsData, healthData] = await Promise.all([
          statsRes.json(),
          healthRes.json()
        ]);

        setStats(statsData);
        setHistory(healthData);
      } catch {
      } finally {
        setIsLoading(false);
      }
    };

    fetchStats();

    return () => {
    };
  }, []);

  return (
    <main className="min-h-screen pt-24 pb-16 px-4">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <h1 className="text-4xl font-medium text-gradient mb-2">System Status</h1>
          <p className="text-muted-foreground">Real-time monitoring and performance metrics</p>
        </div>

        {isLoading ? (
          <div className="space-y-6">
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-3">
              {Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="glass-panel backdrop-blur-sm bg-background/50 p-4 border-2 border-[#8faaa2]/20 animate-pulse">
                  <div className="h-4 w-20 bg-white/10 rounded mb-2" />
                  <div className="h-8 w-32 bg-white/5 rounded" />
                </div>
              ))}
            </div>

            <div className="glass-panel backdrop-blur-sm bg-background/50 py-6 border-2 rounded-3xl border-[#8faaa2]/20 animate-pulse">
              <div className="px-6">
                <div className="flex items-center justify-between mb-5">
                  <div>
                    <div className="h-6 w-24 bg-white/10 rounded mb-2" />
                    <div className="h-4 w-32 bg-white/5 rounded" />
                  </div>
                  <div className="h-8 w-24 bg-white/5 rounded-full" />
                </div>
                <div className="w-full h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
                <div className="grid grid-cols-2 gap-4 mt-5">
                  {Array.from({ length: 4 }).map((_, i) => (
                    <div key={i}>
                      <div className="h-4 w-16 bg-white/10 rounded mb-2" />
                      <div className="h-6 w-24 bg-white/5 rounded" />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="glass-panel backdrop-blur-sm bg-background/50 p-6 border-2 rounded-3xl border-[#8faaa2]/20 animate-pulse">
              <div className="h-6 w-32 bg-white/10 rounded mb-6" />
              <div className="space-y-8">
                <div>
                  <div className="h-4 w-24 bg-white/10 rounded mb-4" />
                  <div className="h-48 bg-[#8faaa2]/5 rounded-xl" />
                </div>
                <div>
                  <div className="h-4 w-24 bg-white/10 rounded mb-4" />
                  <div className="h-48 bg-[#8faaa2]/5 rounded-xl" />
                </div>
              </div>
            </div>
          </div>
        ) : stats ? (
          <div className="space-y-6">
            <div className="grid gap-4 grid-cols-1 sm:grid-cols-3">
              <StatCard
                label="Total Servers"
                value={stats.guilds.toLocaleString()}
                className="bg-background/50 border-2 border-[#8faaa2]/20"
              />
              <StatCard
                label="Total Users"
                value={stats.users.toLocaleString()}
                className="bg-background/50 border-2 border-[#8faaa2]/20"
              />
              <StatCard
                label="Uptime"
                value={stats.uptime}
                className="bg-background/50 border-2 border-[#8faaa2]/20"
              />
            </div>

            <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
              {Object.entries(stats.shard_stats).map(([id, shard]) => (
                <div key={id} className="glass-panel backdrop-blur-sm bg-background/50 py-6 border-2 rounded-3xl border-[#8faaa2]/20">
                  <div className="px-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-xl font-semibold">Shard {shard.id}</p>
                        <p className="mt-1 text-xs font-medium text-neutral-400 inline-flex items-center">
                          <HiClock className="inline-block h-3 w-3 mr-2" />
                          {formatDistanceToNow(new Date(stats.timestamp + 'Z'), { addSuffix: true }).replace('about ', '')}
                        </p>
                      </div>
                      <span className={`text-sm inline-flex items-center font-medium py-1 px-2.5 rounded-full border border-white/10 bg-background/50 ${shard.latency < 100 ? "text-green-500" : shard.latency < 200 ? "text-yellow-500" : "text-red-500"}`}>
                        {shard.latency < 100 ? (
                          <HiSignal className="mr-1 h-4 w-4 text-green-500" />
                        ) : shard.latency < 200 ? (
                          <HiSignal className="mr-1 h-4 w-4 text-yellow-500" />
                        ) : (
                          <HiSignal className="mr-1 h-4 w-4 text-red-500" />
                        )}
                        Operational
                      </span>
                    </div>
                  </div>

                  <div className="w-full h-px my-5 bg-gradient-to-r from-transparent via-white/10 to-transparent" />

                  <div className="grid grid-cols-2 gap-4 px-6 font-medium text-sm">
                    <div>
                      <p className="font-medium text-neutral-400 text-sm">Latency</p>
                      <p className="font-medium text-white mt-1 inline-flex items-center">
                        <HiWifi className="inline-block mr-2 h-4 w-4 text-neutral-400" />
                        {Math.round(shard.latency)}ms
                      </p>
                    </div>
                    <div>
                      <p className="font-medium text-neutral-400 text-sm">Uptime</p>
                      <p className="font-medium text-white mt-1 inline-flex items-center">
                        <HiCube className="inline-block mr-2 h-4 w-4 text-neutral-400" />
                        {stats.uptime}
                      </p>
                    </div>
                    <div>
                      <p className="font-medium text-neutral-400 text-sm">Servers</p>
                      <p className="font-medium text-white mt-1 inline-flex items-center">
                        <HiServerStack className="inline-block h-4 w-4 mr-2 text-neutral-400" />
                        {shard.guilds.toLocaleString()}
                      </p>
                    </div>

                    <div>
                      <p className="font-medium text-neutral-400 text-sm">Users</p>
                      <p className="font-medium text-white mt-1 inline-flex items-center">
                        <HiUsers className="inline-block h-4 w-4 mr-2 text-neutral-400" />
                        {shard.users.toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {history && (
              <div className="mt-10">
                <div className="glass-panel backdrop-blur-sm bg-background/50 p-6 border-2 rounded-3xl border-[#8faaa2]/20">
                  <h3 className="text-xl font-semibold mb-6">Tempt's growth</h3>

                  <div className="mb-8">
                    <h4 className="text-neutral-400 text-sm font-medium mb-4">Server Growth</h4>
                    <div className="bg-[#8faaa2]/5 rounded-xl p-4">
                      <AnalyticsGraph data={history.history} metric="guild_count" />
                    </div>
                  </div>

                  <div>
                    <h4 className="text-neutral-400 text-sm font-medium mb-4">User Growth</h4>
                    <div className="bg-[#8faaa2]/5 rounded-xl p-4">
                      <AnalyticsGraph data={history.history} metric="total_members" />
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="bg-background/50 border-2 rounded-3xl border-destructive/20 p-8 text-center">
            <div className="mb-2 text-xl">Unable to fetch status</div>
            <p className="text-muted-foreground text-sm">Please try again later</p>
          </div>
        )}
      </div>
    </main>
  );
}

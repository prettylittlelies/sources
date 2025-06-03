import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import { useState } from "react";
import numeral from "numeral";

const formatValue = (value: number) => {
  return numeral(value).format('0.[0]a');
};

const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).toLowerCase();
};

interface HistoryPoint {
  guild_count: number;
  total_members: number;
  status: string;
  timestamp: string;
}

interface AnalyticsGraphProps {
  data: HistoryPoint[];
  metric: "guild_count" | "total_members";
  className?: string;
}

const TIME_RANGES = {
  "12h": 12,
  "24h": 24,
  "7d": 168,
} as const;

type TimeRange = keyof typeof TIME_RANGES;

const generateTimePoints = (hours: number) => {
  const points = [];
  const now = new Date();
  for (let i = hours - 1; i >= 0; i--) {
    const time = new Date(now);
    time.setHours(now.getHours() - i);
    time.setMinutes(0);
    time.setSeconds(0);
    time.setMilliseconds(0);
    points.push(time.toISOString());
  }
  return points;
};

const fillMissingData = (
  data: HistoryPoint[],
  timeRange: TimeRange,
  metric: "guild_count" | "total_members",
) => {
  const hours = TIME_RANGES[timeRange];
  const timePoints = generateTimePoints(hours);
  const sortedData = [...data].sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime(),
  );

  return timePoints
    .map((timestamp) => {
      const pointTime = new Date(timestamp).getTime();

      const closestPoint = sortedData.reduce(
        (closest, current) => {
          const currentDiff = Math.abs(
            new Date(current.timestamp).getTime() - pointTime,
          );
          const closestDiff = closest
            ? Math.abs(new Date(closest.timestamp).getTime() - pointTime)
            : Infinity;
          return currentDiff < closestDiff ? current : closest;
        },
        null as HistoryPoint | null,
      );

      return {
        timestamp,
        value: closestPoint?.[metric] ?? null,
      };
    })
    .filter((point) => point.value !== null);
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    const currentValue = payload[0].value;
    const previousValue = payload[1]?.value;
    const change = previousValue ? currentValue - previousValue : 0;
    const changePercent = previousValue ? ((change / previousValue) * 100).toFixed(1) : 0;

    return (
      <div className="glass-panel px-4 py-3 border-[#8faaa2]/20">
        <p className="text-sm font-medium text-white/80">
          {formatTime(label)}
        </p>
        <p className="text-xl font-medium text-white mt-1">
          {currentValue.toLocaleString()}
        </p>
        {change !== 0 && (
          <p className={cn("text-sm font-medium mt-1", change > 0 ? "text-emerald-400" : "text-red-400")}>
            {change > 0 ? "↑" : "↓"} {Math.abs(change).toLocaleString()} ({changePercent}%)
          </p>
        )}
      </div>
    );
  }
  return null;
};

export function AnalyticsGraph({
  data,
  metric,
  className,
}: AnalyticsGraphProps) {
  const [timeRange, setTimeRange] = useState<TimeRange>("24h");
  const chartData = fillMissingData(data, timeRange, metric);

  return (
    <div className={className}>
      <div className="flex justify-between items-center mb-4">
        <div className="flex gap-2">
          {Object.keys(TIME_RANGES).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range as TimeRange)}
              className={cn(
                "px-3 py-1.5 rounded-md text-sm font-medium transition-all duration-200",
                timeRange === range
                  ? "bg-[#8faaa2]/10 text-[#8faaa2] border-[#8faaa2]/20"
                  : "text-white/60 hover:text-white/80 hover:bg-white/5"
              )}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      <div className="w-full h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={chartData}
            margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
          >
            <defs>
              <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#8faaa2" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#8faaa2" stopOpacity={0.01} />
              </linearGradient>
            </defs>
            <XAxis
              dataKey="timestamp"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 12 }}
              dy={10}
              tickFormatter={(value: string) => formatTime(value)}
            />
            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "rgba(255,255,255,0.4)", fontSize: 12 }}
              dx={-10}
              tickFormatter={formatValue}
            />
            <Tooltip content={<CustomTooltip />} cursor={false} />
            <Area
              type="monotone"
              dataKey="value"
              stroke="#8faaa2"
              strokeWidth={1.5}
              fill="url(#colorValue)"
              dot={false}
              activeDot={{
                r: 4,
                fill: "#050505",
                stroke: "#8faaa2",
                strokeWidth: 1.5,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

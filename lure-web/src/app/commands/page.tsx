"use client";

import { Command, CommandCategory } from "@/types/commands";
import { CommandCard } from "@/components/ui/command-card";
import { useState, useMemo, useEffect } from "react";
import { MagnifyingGlassIcon } from "@radix-ui/react-icons";
import { categories } from "@/data/categories";

let commandsCache: Command[] | null = null;

export default function CommandsPage() {
  const [activeCategory, setActiveCategory] = useState<CommandCategory>("All");
  const [searchQuery, setSearchQuery] = useState("");
  const [commands, setCommands] = useState<Command[]>(commandsCache || []);
  const [isLoading, setIsLoading] = useState(!commandsCache);

  useEffect(() => {
    const fetchCommands = async () => {
      if (commandsCache) {
        return;
      }

      try {
        const response = await fetch("https://s3.tempt.lol/min/cmds.json");
        const data = await response.json();
        commandsCache = data;
        setCommands(data);
      } catch (error) {
        console.error("Failed to fetch commands:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCommands();
  }, []);

  const filteredCommands = useMemo(() => {
    if (!commands) return [];

    const hiddenCategories = ["Jishaku", "Developer"];
    const visibleCommands = commands.filter((cmd) => {
      if (hiddenCategories.includes(cmd.cog)) return false;

      const isParentCommand = commands.some(
        (other) =>
          other.name.startsWith(cmd.name + " ") && other.name !== cmd.name,
      );
      if (isParentCommand) return false;

      return true;
    });

    const commandsToFilter =
      activeCategory === "All"
        ? visibleCommands
        : visibleCommands.filter((cmd) => cmd.cog === activeCategory);

    return commandsToFilter
      .filter(
        (command) =>
          command.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          command.description
            .toLowerCase()
            .includes(searchQuery.toLowerCase()) ||
          command.aliases?.some((alias) =>
            alias.toLowerCase().includes(searchQuery.toLowerCase()),
          ),
      )
      .sort((a, b) => a.name.localeCompare(b.name));
  }, [activeCategory, searchQuery, commands]);

  const categoryCommandCounts = useMemo(() => {
    if (!commands) return {};

    const hiddenCategories = ["Jishaku", "Developer"];
    const visibleCommands = commands.filter(
      (cmd) => !hiddenCategories.includes(cmd.cog),
    );

    return visibleCommands.reduce(
      (acc, command) => {
        acc[command.cog] = (acc[command.cog] || 0) + 1;
        return acc;
      },
      {} as Record<string, number>,
    );
  }, [commands]);

  return (
    <main className="relative pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-4 space-y-10">
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-gradient mb-2">Commands</h1>
          <p className="text-muted-foreground">
            Browse and search through all available commands.
          </p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          <div className="w-full lg:w-72 lg:flex-shrink-0">
            <div className="lg:sticky lg:top-32 space-y-6">
              <div className="relative">
                <div className="absolute inset-0 backdrop-blur-xl bg-background/50 rounded-md border border-white/10" />
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-white/70 pointer-events-none z-10" />
                <input
                  placeholder="Search commands..."
                  className="relative w-full bg-transparent pl-12 pr-4 py-3 text-sm text-white placeholder:text-white/40 focus:outline-none z-10"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="glass-panel backdrop-blur-sm bg-background/50 p-5">
                <h3 className="text-sm font-medium mb-4 text-white/80">
                  Categories
                </h3>
                <div className="space-y-1.5">
                  {categories.map((category) => {
                    const commandCount =
                      category.name === "All"
                        ? commands.length
                        : categoryCommandCounts[category.name] || 0;

                    return (
                      <button
                        key={category.name}
                        onClick={() => setActiveCategory(category.name)}
                        className={`
                          group w-full flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors
                          ${
                            activeCategory === category.name
                              ? "bg-white/10 text-white"
                              : "text-white/60 hover:text-white hover:bg-white/5"
                          }
                        `}
                      >
                        <span className="flex items-center gap-2">
                          {category.icon}
                          {category.name}
                        </span>
                        <span
                          className={`text-xs tabular-nums ${
                            activeCategory === category.name
                              ? "text-white/60"
                              : "text-white/40 group-hover:text-white/50"
                          }`}
                        >
                          {commandCount}
                        </span>
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          <div className="flex-1 space-y-2">
            {isLoading ? (
              Array.from({ length: 3 }).map((_, i) => (
                <CommandCard
                  key={i}
                  command={{
                    name: "",
                    description: "",
                    cog: "",
                    aliases: [],
                    usage: "",
                    parameters: [],
                  }}
                  isLoading
                />
              ))
            ) : filteredCommands?.length > 0 ? (
              filteredCommands.map((command) => (
                <CommandCard key={command.name} command={command} />
              ))
            ) : searchQuery || activeCategory !== "All" ? (
              <div className="glass-panel backdrop-blur-sm bg-background/50 p-6 text-center">
                <p className="text-white/60">
                  No commands found matching your search.
                </p>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </main>
  );
}

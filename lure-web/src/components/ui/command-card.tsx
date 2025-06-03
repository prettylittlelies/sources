"use client";

import { useState, useEffect } from "react";
import { CopyIcon, ChevronDownIcon } from "@radix-ui/react-icons";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

interface CommandCardProps {
  command?: Command;
  isLoading?: boolean;
}

interface CommandParameter {
  name: string;
  required: boolean;
}

interface Command {
  name: string;
  description: string;
  aliases: string[];
  usage: string;
  parameters: CommandParameter[];
  cog: string;
}

export function CommandCard({ command, isLoading }: CommandCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [prevLoading, setPrevLoading] = useState(isLoading);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const formattedName = command?.name ? `/${command.name}` : "";

  const hasParameters = command?.parameters && command.parameters.length > 0;
  const hasDescription =
    command?.description && command.description !== "No description provided";
  const hasContent = hasDescription || hasParameters || command?.usage;

  const copyCommand = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (command) {
      navigator.clipboard.writeText(`,${command.name}`);
      toast.success("Command copied to clipboard");
    }
  };

  useEffect(() => {
    if (prevLoading && !isLoading) {
      setIsTransitioning(true);
      const timer = setTimeout(() => setIsTransitioning(false), 300);
      return () => clearTimeout(timer);
    }
    setPrevLoading(isLoading);
  }, [isLoading, prevLoading]);

  if (isLoading) {
    return (
      <div className="glass-panel backdrop-blur-sm bg-background/50 p-6">
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="h-5 w-24 bg-white/10 rounded" />
                <div className="h-5 w-16 bg-white/10 rounded" />
              </div>
              <div className="mt-2 h-4 w-3/4 bg-white/10 rounded" />
            </div>
            <div className="h-8 w-8 bg-white/10 rounded-md" />
          </div>
        </div>
      </div>
    );
  }

  if (!command) return null;

  return (
    <div
      className={`
        glass-panel backdrop-blur-sm bg-background/50 overflow-hidden ${
          hasContent ? "cursor-pointer" : ""
        } transition-all duration-200
        ${
          isExpanded
            ? "ring-1 ring-white/10"
            : hasContent
              ? "hover:bg-background/60"
              : ""
        }
      `}
      onClick={() => (hasContent ? setIsExpanded(!isExpanded) : null)}
    >
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <div>
                <h3 className="text-base font-medium">{formattedName}</h3>
              </div>
              <button
                onClick={copyCommand}
                className="p-1 rounded-md transition-colors hover:bg-white/10 active:bg-white/15"
                aria-label="Copy command"
              >
                <CopyIcon className="text-white/40 hover:text-white/70 h-3 w-3 transition-colors" />
              </button>
            </div>
            {hasDescription && (
              <p className="text-sm text-muted-foreground mt-1.5">
                {command.description}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2">
            {command.aliases && command.aliases.length > 0 && (
              <div className="flex flex-wrap gap-1 items-start">
                {command.aliases.map((alias) => (
                  <span
                    key={alias}
                    className="px-1.5 py-0.5 rounded text-xs font-medium bg-white/5 text-white/60"
                  >
                    {alias}
                  </span>
                ))}
              </div>
            )}

            {hasContent && (
              <ChevronDownIcon
                className={`
                text-white/40 h-4 w-4 shrink-0 transition-transform duration-200
                ${isExpanded ? "rotate-180" : ""}
              `}
              />
            )}
          </div>
        </div>
      </div>
      <AnimatePresence initial={false}>
        {isExpanded && hasContent && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 pb-4 border-t border-white/5 pt-3">
              {command.usage && (
                <div className="space-y-2">
                  <h4 className="text-xs font-medium text-white/80">Usage</h4>
                  <div className="p-2 rounded-md bg-background/40 border border-white/5">
                    <code className="text-sm text-white/80 font-mono">
                      /{command.name} {command.usage}
                    </code>
                  </div>
                </div>
              )}

              {hasParameters && (
                <div className="mt-4 space-y-2">
                  <h4 className="text-xs font-medium text-white/80">
                    Parameters
                  </h4>
                  <div className="space-y-2">
                    {Array.isArray(command.parameters) &&
                      command.parameters.map((param, index) => (
                        <div
                          key={`${command.name}-${param.name}-${index}`}
                          className="p-2 rounded-md bg-background/40 border border-white/5 flex items-center justify-between"
                        >
                          <code className="text-sm text-white/80 font-mono">
                            {param.name}
                          </code>
                          <span
                            className={cn(
                              "text-xs px-2.5 py-1 rounded-full backdrop-blur-sm transition-colors",
                              param.required
                                ? "bg-[#8faaa2]/10 text-[#8faaa2] border border-[#8faaa2]/20 shadow-[#8faaa2]/5 shadow-sm"
                                : "bg-white/5 text-white/60 border border-white/10",
                            )}
                          >
                            {param.required ? "Required" : "Optional"}
                          </span>
                        </div>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

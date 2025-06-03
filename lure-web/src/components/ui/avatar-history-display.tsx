"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import {
  Container,
  Box,
  Text,
  Dialog,
  AspectRatio,
  Button,
} from "@radix-ui/themes";
import {
  ExclamationTriangleIcon,
  Link2Icon,
  DownloadIcon,
} from "@radix-ui/react-icons";
import { motion, AnimatePresence } from "framer-motion";

interface AvatarData {
  url: string;
  lastModified: string;
}

interface AvatarHistoryDisplayProps {
  userId: string;
  page: number;
  totalCount: number;
  initialAvatars?: AvatarData[];
  initialUsername?: string;
}

export function AvatarHistoryDisplay({
  userId,
  page,
  totalCount,
  initialAvatars = [],
  initialUsername,
}: AvatarHistoryDisplayProps) {
  const [avatars, setAvatars] = useState<AvatarData[]>(initialAvatars);
  const [isLoading, setIsLoading] = useState(!initialAvatars.length);
  const [username, setUsername] = useState<string | null>(
    initialUsername || null,
  );
  const [selectedAvatar, setSelectedAvatar] = useState<AvatarData | null>(null);
  const [imageLoadStates, setImageLoadStates] = useState<
    Record<string, "loading" | "loaded" | "error">
  >({});

  const handleImageLoad = (url: string) => {
    setImageLoadStates((prev) => ({ ...prev, [url]: "loaded" }));
  };

  const handleImageError = (url: string) => {
    setImageLoadStates((prev) => ({ ...prev, [url]: "error" }));
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return "";
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    }).format(date);
  };

  const copyImageLink = (url: string) => {
    navigator.clipboard.writeText(url);
  };

  const downloadImage = async (url: string) => {
    const response = await fetch(url);
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = blobUrl;
    link.download = `avatar-${new Date().getTime()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(blobUrl);
  };

  useEffect(() => {
    setIsLoading(true);
    setAvatars(initialAvatars);
    setUsername(initialUsername || null);
    const states: Record<string, "loading" | "loaded" | "error"> = {};
    initialAvatars.forEach((avatar) => {
      states[avatar.url] = "loading";
    });
    setImageLoadStates(states);
    setIsLoading(false);
  }, [initialAvatars, initialUsername, page]);

  useEffect(() => {
    const fetchData = async () => {
      if (initialAvatars.length > 0 && initialUsername) {
        setIsLoading(false);
        return;
      }

      try {
        const res = await fetch(`/api/avatarhistory/${userId}`);
        const data = await res.json();

        if (res.ok && data.avatars?.length > 0) {
          setAvatars(data.avatars);
          setUsername(data.username);
          const states: Record<string, "loading" | "loaded" | "error"> = {};
          data.avatars.forEach((avatar: AvatarData) => {
            states[avatar.url] = "loading";
          });
          setImageLoadStates(states);
        } else {
          setAvatars([]);
        }
      } catch {
        setAvatars([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [userId, initialAvatars, initialUsername]);

  return (
    <Container>
      <Box className="glass-panel backdrop-blur-sm bg-background/50 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 sm:gap-0 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            <Text size="2" color="gray">
              {totalCount} {totalCount === 1 ? "avatar" : "avatars"} collected
            </Text>
            {Math.ceil(totalCount / 20) > 1 && (
              <>
                <span className="opacity-10">•</span>
                <Text size="2" color="gray">
                  {page}/{Math.ceil(totalCount / 20)}
                </Text>
              </>
            )}
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-2">
                <Button
                style={{
                  backgroundColor: "#8faaa2",
                  color: "#1a1a1a",
                  border: "none",
                }}
                className="p-2"
                disabled={page <= 1}
                asChild={page > 1}
                >
                {page > 1 ? (
                  <Link href={`/avatarhistory/${userId}?p=${page - 1}`}>←</Link>
                ) : (
                  <span>←</span>
                )}
                </Button>
                <Button
                style={{
                  backgroundColor: "#8faaa2",
                  color: "#1a1a1a",
                  border: "none",
                }}
                className="p-2"
                disabled={page >= Math.ceil(totalCount / 20)}
                asChild={page < Math.ceil(totalCount / 20)}
                >
                {page < Math.ceil(totalCount / 20) ? (
                  <Link href={`/avatarhistory/${userId}?p=${page + 1}`}>→</Link>
                ) : (
                  <span>→</span>
                )}
                </Button>
            </div>
            <div className="flex items-center gap-2">
              <span className="opacity-10">•</span>
              <Button
                style={{
                  backgroundColor: "#8faaa2",
                  color: "#1a1a1a",
                  border: "none"
                }}
                asChild
              >
                <Link
                  href={`https://discord.com/users/${userId}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2"
                >
                  View Profile →
                </Link>
              </Button>
            </div>
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <AspectRatio key={i} ratio={1}>
                <div className="w-full h-full rounded-lg bg-white/10 animate-pulse" />
              </AspectRatio>
            ))}
          </div>
        ) : avatars.length === 0 ? (
          <div className="text-center py-12">
            <Text size="3" color="gray" className="text-muted-foreground">
              {username === null
                ? "This user doesn't exist or hasn't been tracked yet"
                : "No avatars found"}
            </Text>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-6">
              {avatars.map((avatar, index) => (
                <AspectRatio key={index} ratio={1}>
                  <button
                    onClick={() => setSelectedAvatar(avatar)}
                    className="w-full h-full relative group"
                  >
                    {imageLoadStates[avatar.url] !== "loaded" &&
                      imageLoadStates[avatar.url] !== "error" && (
                        <div className="absolute inset-0 z-10 rounded-lg bg-white/10 animate-pulse" />
                      )}
                    {imageLoadStates[avatar.url] === "error" ? (
                      <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-background/50">
                        <ExclamationTriangleIcon className="w-6 h-6 text-gray-400" />
                      </div>
                    ) : (
                      <div className="relative w-full h-full">
                        <Image
                          src={avatar.url}
                          alt={`${username}'s avatar ${index + 1}`}
                          className="rounded-lg transition-all duration-700 ring-1 ring-white/10 hover:ring-2 hover:ring-white/20 hover:shadow-[0_0_15px_rgba(103,145,229,0.15)]"
                          fill
                          sizes="(max-width: 640px) 50vw, (max-width: 768px) 33vw, 25vw"
                          onLoad={() => handleImageLoad(avatar.url)}
                          onError={() => handleImageError(avatar.url)}
                          style={{
                            opacity: imageLoadStates[avatar.url] === "loaded" ? 1 : 0,
                            transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)"
                          }}
                        />
                        {imageLoadStates[avatar.url] === "loaded" && avatar.lastModified && (
                          <div className="absolute inset-x-0 bottom-0 bg-background/50 backdrop-blur-sm opacity-0 group-hover:opacity-100 transition-all duration-700 rounded-b-lg border-t border-white/5">
                            <Text size="1" className="text-white/90 text-center py-2">
                              {formatDate(avatar.lastModified)}
                            </Text>
                          </div>
                        )}
                      </div>
                    )}
                  </button>
                </AspectRatio>
              ))}
            </div>
          </div>
        )}
      </Box>

      <Dialog.Root open={!!selectedAvatar} onOpenChange={() => setSelectedAvatar(null)}>
        <Dialog.Content className="fixed inset-0 z-50 flex items-center justify-center data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out data-[state=open]:fade-in data-[state=closed]:slide-out-to-bottom-4 data-[state=open]:slide-in-from-bottom-4 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[state=open]:duration-700 data-[state=closed]:duration-300 !p-0 !overflow-hidden" style={{ maxWidth: "min(90vw, 600px)" }}>
          <Dialog.Title className="sr-only">{username}'s Avatar</Dialog.Title>
          {selectedAvatar && (
            <AspectRatio ratio={1} style={{ maxHeight: "90vh" }}>
              <div className="relative w-full h-full">
                {imageLoadStates[selectedAvatar.url] === "loading" && (
                  <div className="absolute inset-0 rounded-lg bg-white/10 animate-pulse" />
                )}
                {imageLoadStates[selectedAvatar.url] === "error" ? (
                  <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-background/50">
                    <ExclamationTriangleIcon className="w-12 h-12 text-gray-400" />
                  </div>
                ) : (
                  <>
                    <Image
                      src={selectedAvatar.url}
                      alt={`${username}'s avatar`}
                      fill
                      className="rounded-lg ring-[3px] ring-white/20 shadow-[0_0_30px_rgba(103,145,229,0.2)]"
                      sizes="(max-width: 600px) 90vw, 600px"
                      priority
                      style={{
                        opacity: imageLoadStates[selectedAvatar.url] === "loaded" ? 1 : 0
                      }}
                    />
                    <div className="absolute top-4 right-4 flex gap-2">
                      <button onClick={() => copyImageLink(selectedAvatar.url)} className="p-2 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 transition-all hover:bg-white/10" title="Copy link">
                        <Link2Icon className="w-4 h-4 text-white/90" />
                      </button>
                      <button onClick={() => downloadImage(selectedAvatar.url)} className="p-2 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 transition-all hover:bg-white/10" title="Download">
                        <DownloadIcon className="w-4 h-4 text-white/90" />
                      </button>
                    </div>
                    {selectedAvatar.lastModified && (
                      <div className="absolute inset-x-0 bottom-0 bg-background/50 backdrop-blur-sm rounded-b-lg border-t-[2px] border-white/10">
                        <Text size="2" className="text-white/90 text-left py-3 px-4">{formatDate(selectedAvatar.lastModified)}</Text>
                      </div>
                    )}
                  </>
                )}
              </div>
            </AspectRatio>
          )}
        </Dialog.Content>
      </Dialog.Root>
    </Container>
  );
}

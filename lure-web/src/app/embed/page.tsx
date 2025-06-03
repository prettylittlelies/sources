"use client";

import { useState } from "react";
import {
  Button,
  Container,
  Flex,
  Grid,
  Heading,
  Text,
  TextArea,
  Box,
} from "@radix-ui/themes";
import {
  PlusIcon,
  CopyIcon,
  DownloadIcon,
  InfoCircledIcon,
  FileIcon,
  Cross2Icon,
  ChevronDownIcon,
} from "@radix-ui/react-icons";
import * as Dialog from "@radix-ui/react-dialog";
import * as Collapsible from "@radix-ui/react-collapsible";
import { toast } from "sonner";
import tinycolor from "tinycolor2";
import { motion, AnimatePresence } from "framer-motion";

interface EmbedForm {
  content?: string;
  color?: string;
  author?: {
    name?: string;
    icon_url?: string;
    url?: string;
  };
  title?: string;
  url?: string;
  description?: string;
  thumbnail?: string;
  image?: string;
  footer?: {
    text?: string;
    icon_url?: string;
  };
  fields: Array<{
    name: string;
    value: string;
    inline: boolean;
  }>;
  buttons: Array<{
    label?: string;
    url?: string;
    style?: "red" | "green" | "gray" | "blue";
    emoji?: string;
    disabled?: boolean;
  }>;
}

const variables = {
  "{user}": "Tempt",
  "{user.mention}": "@Tempt",
  "{member.mention}": "@Tempt",
  "{user.name}": "Tempt",
  "{user.id}": "1132607680163352627",
  "{member.id}": "1132607680163352627",
  "{member.name}": "Tempt",
  "{user.avatar}":
    "https://cdn.discordapp.com/avatars/427856906399154196/a_d4b8d0d355555555.png",
  "{member.avatar}":
    "https://cdn.discordapp.com/avatars/427856906399154196/a_d4b8d0d355555555.png",
  "{user.joined_at}": "March 15, 2024",
  "{member.joined_at}": "March 15, 2024",
  "{user.created_at}": "March 10, 2023",
  "{member.created_at}": "March 10, 2023",
  "{guild.name}": "Tempt Bot",
  "{guild.count}": "15234",
  "{guild.count.format}": "15,234",
  "{guild.id}": "987654321098765432",
  "{guild.created_at}": "January 1, 2023",
  "{guild.boost_count}": "42",
  "{guild.booster_count}": "38",
  "{guild.boost_count.format}": "42",
  "{guild.booster_count.format}": "38",
  "{guild.boost_tier}": "3",
  "{guild.vanity}": "Temptbot",
  "{invisible}": "",
  "{botcolor}": "#5865F2",
  "{guild.icon}":
    "https://cdn.discordapp.com/icons/987654321098765432/a_1234567890.png",
};

const markdownExample = `You can use Discord markdown:
**Bold** or __Bold__
*Italic* or _Italic_
***Bold Italic*** or **_Bold Italic_**
__*Bold Italic*__ or **_Bold Italic_**
~~Strikethrough~~
\`Code\`
\`\`\`
Code block
Multiple lines
\`\`\`
> Quote
>>> Multi-line quote
||Spoiler||
# Header 1
## Header 2`;

const variablesExample = Object.entries(variables)
  .map(([key, value]) => `${key}\n  Example: ${value}`)
  .join("\n\n");

export default function EmbedBuilder() {
  const [showMarkdownGuide, setShowMarkdownGuide] = useState(false);
  const [showVariablesGuide, setShowVariablesGuide] = useState(false);
  const [showImportDialog, setShowImportDialog] = useState(false);
  const [importText, setImportText] = useState("");
  const [form, setForm] = useState<EmbedForm>({
    content: "",
    color: "#8faaa2",
    author: {
      name: "",
      icon_url: "",
      url: "",
    },
    title: "",
    url: "",
    description: "",
    thumbnail: "",
    image: "",
    footer: {
      text: "",
      icon_url: "",
    },
    fields: [],
    buttons: [],
  });
  const [openSections, setOpenSections] = useState({
    general: true,
    author: false,
    fields: false,
    buttons: false,
    footer: false,
  });

  const generateCode = () => {
    let code = "{embed}";

    if (form.content) code += `$v{content: ${form.content}}`;
    if (form.color) code += `$v{color: ${form.color}}`;
    if (form.title) code += `$v{title: ${form.title}}`;
    if (form.description) code += `$v{description: ${form.description}}`;
    if (form.url) code += `$v{url: ${form.url}}`;
    if (form.thumbnail) code += `$v{thumbnail: ${form.thumbnail}}`;
    if (form.image) code += `$v{image: ${form.image}}`;

    if (form.author?.name) {
      code += `$v{author: ${form.author.name}`;
      if (form.author.icon_url) code += ` && ${form.author.icon_url}`;
      if (form.author.url) code += ` && ${form.author.url}`;
      code += "}";
    }

    if (form.footer?.text) {
      code += `$v{footer: ${form.footer.text}`;
      if (form.footer.icon_url) code += ` && ${form.footer.icon_url}`;
      code += "}";
    }

    form.fields.forEach((field) => {
      code += `$v{field: ${field.name} && ${field.value} && ${field.inline}}`;
    });

    form.buttons.forEach((button) => {
      let buttonCode = "button: label:" + (button.label || "Button");
      if (button.url) buttonCode += ` && url: ${button.url}`;
      if (button.style) buttonCode += ` && style: ${button.style}`;
      if (button.emoji) buttonCode += ` && emoji: ${button.emoji}`;
      if (button.disabled) buttonCode += " && disabled";
      code += `$v{${buttonCode}}`;
    });

    return code;
  };

  const copyCode = () => {
    const code = generateCode();
    navigator.clipboard.writeText(code);
    toast.success("Embed code copied to clipboard");
  };

  const handleColorChange = (color: string) => {
    if (tinycolor(color).isValid()) {
      setForm((prev) => ({ ...prev, color }));
    }
  };

  const addField = () => {
    setForm((prev) => ({
      ...prev,
      fields: [...prev.fields, { name: "", value: "", inline: false }],
    }));
  };

  const removeField = (index: number) => {
    setForm((prev) => ({
      ...prev,
      fields: prev.fields.filter((_, i) => i !== index),
    }));
  };

  const addButton = () => {
    setForm((prev) => ({
      ...prev,
      buttons: [...prev.buttons, { label: "", style: "gray" }],
    }));
  };

  const removeButton = (index: number) => {
    setForm((prev) => ({
      ...prev,
      buttons: prev.buttons.filter((_, i) => i !== index),
    }));
  };

  const formatDiscordMarkdown = (text: string) => {
    if (!text) return text;

    text = text.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    text = text.replace(/__(.*?)__/g, "<strong>$1</strong>");
    text = text.replace(/\*(.*?)\*/g, "<em>$1</em>");
    text = text.replace(/_(.*?)_/g, "<em>$1</em>");
    text = text.replace(/~~(.*?)~~/g, "<del>$1</del>");
    text = text.replace(
      /\`\`\`([\s\S]*?)\`\`\`/g,
      "<pre><code>$1</code></pre>",
    );
    text = text.replace(/\`(.*?)\`/g, "<code>$1</code>");
    text = text.replace(/^>>>\s(.+)$/gm, "<blockquote>$1</blockquote>");
    text = text.replace(/^>\s(.+)$/gm, "<blockquote>$1</blockquote>");
    text = text.replace(/\|\|(.*?)\|\|/g, '<span class="spoiler">$1</span>');
    text = text.replace(/^# (.*$)/gm, "<h1>$1</h1>");
    text = text.replace(/^## (.*$)/gm, "<h2>$1</h2>");
    text = text.replace(/\\n/g, "<br>");
    text = text.replace(/\n/g, "<br>");

    return text;
  };

  const replaceVariables = (text: string) => {
    if (!text) return text;
    return Object.entries(variables).reduce(
      (acc, [key, value]) => acc.replaceAll(key, value),
      text,
    );
  };

  return (
    <main className="min-h-screen pt-24 pb-16 px-4">
      <Container>
        <div className="mb-8">
          <Heading className="text-4xl font-medium text-gradient mb-2">
            Embed Builder
          </Heading>
          <Text className="text-muted-foreground/80">
            Create and customize Discord embeds with a visual editor
          </Text>
        </div>

        <Grid columns={{ initial: "1", lg: "2" }} gap="6">
          <div className="space-y-6">
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/[0.07] to-transparent" />
              <div className="relative z-10">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <Text className="text-lg font-semibold text-gradient block">
                      Embed Settings
                    </Text>
                    <Text className="text-sm text-muted-foreground/80">
                      Configure your embed's appearance and content
                    </Text>
                  </div>
                  <div className="space-y-1">
                    <button
                      onClick={() => setShowMarkdownGuide(true)}
                      className="w-full flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#8faaa2]/[0.07] backdrop-blur-sm border border-[#8faaa2]/10 text-white/90 hover:bg-[#8faaa2]/[0.12] transition-colors text-sm"
                    >
                      <InfoCircledIcon className="w-4 h-4" />
                      Markdown Guide
                    </button>
                    <button
                      onClick={() => setShowVariablesGuide(true)}
                      className="w-full flex items-center gap-2 px-3 py-1.5 rounded-md bg-[#8faaa2]/[0.07] backdrop-blur-sm border border-[#8faaa2]/10 text-white/90 hover:bg-[#8faaa2]/[0.12] transition-colors text-sm"
                    >
                      <CopyIcon className="w-4 h-4" />
                      Variables
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="glass-panel p-4 space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-[#8faaa2]/90 mb-1">
                        Message Content
                      </label>
                      <TextArea
                        value={form.content}
                        onChange={(e) =>
                          setForm((prev) => ({
                            ...prev,
                            content: e.target.value,
                          }))
                        }
                        className="w-full min-h-[80px] px-3 py-2 bg-[#8faaa2]/[0.07] backdrop-blur-sm rounded-lg border border-[#8faaa2]/10 focus:outline-none focus:border-[#8faaa2]/30 text-white resize-y placeholder:text-[#8faaa2]/40"
                        placeholder="Add a message above the embed..."
                      />
                    </div>
                  </div>

                  <Collapsible.Root
                    open={openSections.general}
                    onOpenChange={(open: boolean) =>
                      setOpenSections((prev) => ({ ...prev, general: open }))
                    }
                  >
                    <Collapsible.Trigger className="flex items-center justify-between w-full p-3 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors">
                      <span className="font-medium">General Settings</span>
                      <motion.div
                        initial={false}
                        animate={{ rotate: openSections.general ? 180 : 0 }}
                        transition={{ duration: 0.15, ease: [0.32, 0.72, 0, 1] }}
                      >
                        <ChevronDownIcon />
                      </motion.div>
                    </Collapsible.Trigger>
                    <AnimatePresence initial={false}>
                      {openSections.general && (
                        <Collapsible.Content asChild forceMount>
                          <motion.div
                            initial={{ height: 0, opacity: 0, y: -5 }}
                            animate={{ height: "auto", opacity: 1, y: 0 }}
                            exit={{ height: 0, opacity: 0, y: -5 }}
                            transition={{
                              height: { duration: 0.2, ease: [0.32, 0.72, 0, 1] },
                              opacity: { duration: 0.15, ease: "easeOut" },
                              y: { duration: 0.15, ease: [0.32, 0.72, 0, 1] },
                            }}
                          >
                            <div className="pt-4 space-y-4">
                              <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">
                                  Color
                                </label>
                                <div className="flex gap-2">
                                  <div className="relative">
                                    <button
                                      className="w-10 h-10 rounded border border-white/10"
                                      style={{ backgroundColor: form.color }}
                                      onClick={(e) => {
                                        const input =
                                          document.createElement("input");
                                        input.type = "color";
                                        input.value = form.color || "#1e40af";
                                        input.style.position = "absolute";
                                        input.style.left = "0";
                                        input.style.top = "0";
                                        input.style.width = "100%";
                                        input.style.height = "100%";
                                        input.style.opacity = "0";
                                        input.style.cursor = "pointer";
                                        input.addEventListener("change", (e) => {
                                          handleColorChange(
                                            (e.target as HTMLInputElement).value,
                                          );
                                        });
                                        e.currentTarget.appendChild(input);
                                        input.click();
                                        input.addEventListener("blur", () => {
                                          e.currentTarget.removeChild(input);
                                        });
                                      }}
                                    />
                                  </div>
                                  <input
                                    type="text"
                                    value={form.color}
                                    onChange={(e) =>
                                      handleColorChange(e.target.value)
                                    }
                                    className="flex-1 px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="#1e40af"
                                  />
                                </div>
                              </div>

                              <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">
                                  Title
                                </label>
                                <input
                                  type="text"
                                  value={form.title}
                                  onChange={(e) =>
                                    setForm((prev) => ({
                                      ...prev,
                                      title: e.target.value,
                                    }))
                                  }
                                  className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                  placeholder="Embed title..."
                                />
                              </div>

                              <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">
                                  Description
                                </label>
                                <TextArea
                                  value={form.description}
                                  onChange={(e) =>
                                    setForm((prev) => ({
                                      ...prev,
                                      description: e.target.value,
                                    }))
                                  }
                                  className="w-full min-h-[100px] px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white resize-y"
                                  placeholder="Embed description..."
                                />
                              </div>

                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Thumbnail URL
                                  </label>
                                  <input
                                    type="url"
                                    value={form.thumbnail}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        thumbnail: e.target.value,
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="https://..."
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Image URL
                                  </label>
                                  <input
                                    type="url"
                                    value={form.image}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        image: e.target.value,
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="https://..."
                                  />
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        </Collapsible.Content>
                      )}
                    </AnimatePresence>
                  </Collapsible.Root>

                  <Collapsible.Root
                    open={openSections.author}
                    onOpenChange={(open: boolean) =>
                      setOpenSections((prev) => ({ ...prev, author: open }))
                    }
                  >
                    <Collapsible.Trigger className="flex items-center justify-between w-full p-3 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors">
                      <span className="font-medium">Author Settings</span>
                      <motion.div
                        initial={false}
                        animate={{ rotate: openSections.author ? 180 : 0 }}
                        transition={{ duration: 0.15, ease: [0.32, 0.72, 0, 1] }}
                      >
                        <ChevronDownIcon />
                      </motion.div>
                    </Collapsible.Trigger>
                    <AnimatePresence initial={false}>
                      {openSections.author && (
                        <Collapsible.Content asChild forceMount>
                          <motion.div
                            initial={{ height: 0, opacity: 0, y: -5 }}
                            animate={{ height: "auto", opacity: 1, y: 0 }}
                            exit={{ height: 0, opacity: 0, y: -5 }}
                            transition={{
                              height: { duration: 0.2, ease: [0.32, 0.72, 0, 1] },
                              opacity: { duration: 0.15, ease: "easeOut" },
                              y: { duration: 0.15, ease: [0.32, 0.72, 0, 1] },
                            }}
                          >
                            <div className="pt-4 space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Author Name
                                  </label>
                                  <input
                                    type="text"
                                    value={form.author?.name}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        author: {
                                          ...prev.author,
                                          name: e.target.value,
                                        },
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="Author name..."
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Author Icon URL
                                  </label>
                                  <input
                                    type="url"
                                    value={form.author?.icon_url}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        author: {
                                          ...prev.author,
                                          icon_url: e.target.value,
                                        },
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="https://..."
                                  />
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        </Collapsible.Content>
                      )}
                    </AnimatePresence>
                  </Collapsible.Root>

                  <Collapsible.Root
                    open={openSections.fields}
                    onOpenChange={(open: boolean) =>
                      setOpenSections((prev) => ({ ...prev, fields: open }))
                    }
                  >
                    <Collapsible.Trigger className="flex items-center justify-between w-full p-3 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors">
                      <span className="font-medium">Fields</span>
                      <div className="flex items-center gap-2">
                        <Text size="1" className="text-gray-400">
                          {form.fields.length} fields
                        </Text>
                        <motion.div
                          initial={false}
                          animate={{ rotate: openSections.fields ? 180 : 0 }}
                          transition={{
                            duration: 0.15,
                            ease: [0.32, 0.72, 0, 1],
                          }}
                        >
                          <ChevronDownIcon />
                        </motion.div>
                      </div>
                    </Collapsible.Trigger>
                    <AnimatePresence initial={false}>
                      {openSections.fields && (
                        <Collapsible.Content asChild forceMount>
                          <motion.div
                            initial={{ height: 0, opacity: 0, y: -5 }}
                            animate={{ height: "auto", opacity: 1, y: 0 }}
                            exit={{ height: 0, opacity: 0, y: -5 }}
                            transition={{
                              height: { duration: 0.2, ease: [0.32, 0.72, 0, 1] },
                              opacity: { duration: 0.15, ease: "easeOut" },
                              y: { duration: 0.15, ease: [0.32, 0.72, 0, 1] },
                            }}
                          >
                            <div className="pt-4 space-y-4">
                              <div className="flex justify-end">
                                <button
                                  onClick={addField}
                                  className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-background/50 backdrop-blur-sm border border-white/10 text-white/90 hover:bg-background/70 transition-colors text-sm"
                                >
                                  <PlusIcon className="w-4 h-4" />
                                  Add Field
                                </button>
                              </div>
                              <div className="space-y-4">
                                {form.fields.map((field, i) => (
                                  <div
                                    key={i}
                                    className="glass-panel p-4 space-y-4"
                                  >
                                    <div className="space-y-4">
                                      <div>
                                        <label className="block text-sm font-medium text-gray-400 mb-1">
                                          Field Title
                                        </label>
                                        <div className="flex items-center gap-2">
                                          <input
                                            type="text"
                                            value={field.name}
                                            onChange={(e) => {
                                              const newFields = [...form.fields];
                                              newFields[i].name = e.target.value;
                                              setForm((prev) => ({
                                                ...prev,
                                                fields: newFields,
                                              }));
                                            }}
                                            placeholder="Field Title"
                                            className="flex-1 px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                          />
                                          <div className="flex items-center gap-2 shrink-0">
                                            <input
                                              type="checkbox"
                                              checked={field.inline}
                                              onChange={(e) => {
                                                const newFields = [
                                                  ...form.fields,
                                                ];
                                                newFields[i].inline =
                                                  e.target.checked;
                                                setForm((prev) => ({
                                                  ...prev,
                                                  fields: newFields,
                                                }));
                                              }}
                                              className="w-4 h-4 rounded border-white/10 bg-background/50"
                                              id={`inline-${i}`}
                                            />
                                            <label
                                              htmlFor={`inline-${i}`}
                                              className="text-sm text-gray-400"
                                            >
                                              Inline
                                            </label>
                                          </div>
                                        </div>
                                      </div>

                                      <div>
                                        <label className="block text-sm font-medium text-gray-400 mb-1">
                                          Field Description
                                        </label>
                                        <div className="flex items-start gap-2">
                                          <TextArea
                                            value={field.value}
                                            onChange={(e) => {
                                              const newFields = [...form.fields];
                                              newFields[i].value = e.target.value;
                                              setForm((prev) => ({
                                                ...prev,
                                                fields: newFields,
                                              }));
                                            }}
                                            placeholder="Field Description"
                                            className="flex-1 min-h-[80px] px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white resize-y"
                                          />
                                          <button
                                            onClick={() => removeField(i)}
                                            className="px-2 py-1.5 h-fit text-xs rounded-md bg-red-500/10 hover:bg-red-500/20 text-red-500 transition-colors"
                                          >
                                            Remove
                                          </button>
                                        </div>
                                      </div>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </motion.div>
                        </Collapsible.Content>
                      )}
                    </AnimatePresence>
                  </Collapsible.Root>

                  <Collapsible.Root
                    open={openSections.buttons}
                    onOpenChange={(open: boolean) =>
                      setOpenSections((prev) => ({ ...prev, buttons: open }))
                    }
                  >
                    <Collapsible.Trigger className="flex items-center justify-between w-full p-3 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors">
                      <span className="font-medium">Buttons</span>
                      <div className="flex items-center gap-2">
                        <Text size="1" className="text-gray-400">
                          {form.buttons.length} buttons
                        </Text>
                        <motion.div
                          initial={false}
                          animate={{ rotate: openSections.buttons ? 180 : 0 }}
                          transition={{
                            duration: 0.15,
                            ease: [0.32, 0.72, 0, 1],
                          }}
                        >
                          <ChevronDownIcon />
                        </motion.div>
                      </div>
                    </Collapsible.Trigger>
                    <AnimatePresence initial={false}>
                      {openSections.buttons && (
                        <Collapsible.Content asChild forceMount>
                          <motion.div
                            initial={{ height: 0, opacity: 0, y: -5 }}
                            animate={{ height: "auto", opacity: 1, y: 0 }}
                            exit={{ height: 0, opacity: 0, y: -5 }}
                            transition={{
                              height: { duration: 0.2, ease: [0.32, 0.72, 0, 1] },
                              opacity: { duration: 0.15, ease: "easeOut" },
                              y: { duration: 0.15, ease: [0.32, 0.72, 0, 1] },
                            }}
                          >
                            <div className="pt-4 space-y-4">
                              <div className="flex justify-end">
                                <button
                                  onClick={addButton}
                                  className="flex items-center gap-2 px-3 py-1.5 rounded-md bg-background/50 backdrop-blur-sm border border-white/10 text-white/90 hover:bg-background/70 transition-colors text-sm"
                                >
                                  <PlusIcon className="w-4 h-4" />
                                  Add Button
                                </button>
                              </div>
                              <div className="space-y-4">
                                {form.buttons.map((button, i) => (
                                  <div
                                    key={i}
                                    className="glass-panel p-4 space-y-4"
                                  >
                                    <div className="grid grid-cols-2 gap-4">
                                      <input
                                        type="text"
                                        value={button.label}
                                        onChange={(e) => {
                                          const newButtons = [...form.buttons];
                                          newButtons[i].label = e.target.value;
                                          setForm((prev) => ({
                                            ...prev,
                                            buttons: newButtons,
                                          }));
                                        }}
                                        placeholder="Button Label"
                                        className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                      />
                                      <div className="flex items-center gap-2">
                                        <select
                                          value={button.style}
                                          onChange={(e) => {
                                            const newButtons = [...form.buttons];
                                            newButtons[i].style = e.target
                                              .value as any;
                                            setForm((prev) => ({
                                              ...prev,
                                              buttons: newButtons,
                                            }));
                                          }}
                                          className="flex-1 px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                        >
                                          <option value="gray">Gray</option>
                                          <option value="green">Green</option>
                                          <option value="blue">Blue</option>
                                          <option value="red">Red</option>
                                        </select>
                                        <button
                                          onClick={() => removeButton(i)}
                                          className="px-2 py-1 text-xs rounded bg-red-500/10 hover:bg-red-500/20 text-red-500"
                                        >
                                          Remove
                                        </button>
                                      </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                      <input
                                        type="text"
                                        value={button.url}
                                        onChange={(e) => {
                                          const newButtons = [...form.buttons];
                                          newButtons[i].url = e.target.value;
                                          setForm((prev) => ({
                                            ...prev,
                                            buttons: newButtons,
                                          }));
                                        }}
                                        placeholder="Button URL"
                                        className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                      />
                                      <input
                                        type="text"
                                        value={button.emoji}
                                        onChange={(e) => {
                                          const newButtons = [...form.buttons];
                                          newButtons[i].emoji = e.target.value;
                                          setForm((prev) => ({
                                            ...prev,
                                            buttons: newButtons,
                                          }));
                                        }}
                                        placeholder="Button Emoji"
                                        className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                      />
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <input
                                        type="checkbox"
                                        checked={button.disabled}
                                        onChange={(e) => {
                                          const newButtons = [...form.buttons];
                                          newButtons[i].disabled =
                                            e.target.checked;
                                          setForm((prev) => ({
                                            ...prev,
                                            buttons: newButtons,
                                          }));
                                        }}
                                        className="w-4 h-4 rounded border-white/10 bg-background/50"
                                      />
                                      <span className="text-sm text-gray-400">
                                        Disabled
                                      </span>
                                    </div>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </motion.div>
                        </Collapsible.Content>
                      )}
                    </AnimatePresence>
                  </Collapsible.Root>

                  <Collapsible.Root
                    open={openSections.footer}
                    onOpenChange={(open: boolean) =>
                      setOpenSections((prev) => ({ ...prev, footer: open }))
                    }
                  >
                    <Collapsible.Trigger className="flex items-center justify-between w-full p-3 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors">
                      <span className="font-medium">Footer Settings</span>
                      <motion.div
                        initial={false}
                        animate={{ rotate: openSections.footer ? 180 : 0 }}
                        transition={{ duration: 0.15, ease: [0.32, 0.72, 0, 1] }}
                      >
                        <ChevronDownIcon />
                      </motion.div>
                    </Collapsible.Trigger>
                    <AnimatePresence initial={false}>
                      {openSections.footer && (
                        <Collapsible.Content asChild forceMount>
                          <motion.div
                            initial={{ height: 0, opacity: 0, y: -5 }}
                            animate={{ height: "auto", opacity: 1, y: 0 }}
                            exit={{ height: 0, opacity: 0, y: -5 }}
                            transition={{
                              height: { duration: 0.2, ease: [0.32, 0.72, 0, 1] },
                              opacity: { duration: 0.15, ease: "easeOut" },
                              y: { duration: 0.15, ease: [0.32, 0.72, 0, 1] },
                            }}
                          >
                            <div className="pt-4 space-y-4">
                              <div className="grid grid-cols-2 gap-4">
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Footer Text
                                  </label>
                                  <input
                                    type="text"
                                    value={form.footer?.text}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        footer: {
                                          ...prev.footer,
                                          text: e.target.value,
                                        },
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="Footer text..."
                                  />
                                </div>
                                <div>
                                  <label className="block text-sm font-medium text-gray-400 mb-1">
                                    Footer Icon URL
                                  </label>
                                  <input
                                    type="url"
                                    value={form.footer?.icon_url}
                                    onChange={(e) =>
                                      setForm((prev) => ({
                                        ...prev,
                                        footer: {
                                          ...prev.footer,
                                          icon_url: e.target.value,
                                        },
                                      }))
                                    }
                                    className="w-full px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white"
                                    placeholder="https://..."
                                  />
                                </div>
                              </div>
                            </div>
                          </motion.div>
                        </Collapsible.Content>
                      )}
                    </AnimatePresence>
                  </Collapsible.Root>
                </div>
              </div>
            </div>
          </div>

          <div className="lg:sticky lg:top-24 space-y-6">
            <div className="glass-panel p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-[#8faaa2]/[0.07] to-transparent" />
              <div className="relative z-10">
                <div className="flex flex-col sm:flex-row gap-3 mb-6">
                  <div className="grid grid-cols-3 gap-3 flex-1">
                    <button
                      onClick={() => copyCode()}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 w-full rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors"
                    >
                      <CopyIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Copy</span>
                    </button>
                    <button
                      onClick={() => {
                        const blob = new Blob([generateCode()], {
                          type: "text/plain",
                        });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement("a");
                        a.href = url;
                        a.download = "embed.txt";
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                        toast.success("Embed exported successfully");
                      }}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 w-full rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors"
                    >
                      <DownloadIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Export</span>
                    </button>
                    <button
                      onClick={() => setShowImportDialog(true)}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 w-full rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors"
                    >
                      <FileIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Import</span>
                    </button>
                  </div>
                </div>

                <div className="bg-[#36393f] rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <img
                      src="https://s3.tempt.lol/min/av.png"
                      alt="Bot Avatar"
                      className="w-10 h-10 rounded-full"
                    />
                    <div className="flex items-center gap-1.5">
                      <span className="text-white font-medium">Tempt</span>
                      <div className="flex items-center bg-[#5865F2] text-white text-xs font-medium px-1 rounded">
                        <svg
                          className="w-3.5 h-3.5 mr-0.5"
                          aria-label="Verified Bot"
                          aria-hidden="false"
                          role="img"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                        >
                          <path
                            fill="currentColor"
                            fillRule="evenodd"
                            d="M19.06 6.94a1.5 1.5 0 0 1 0 2.12l-8 8a1.5 1.5 0 0 1-2.12 0l-4-4a1.5 1.5 0 0 1 2.12-2.12L10 13.88l6.94-6.94a1.5 1.5 0 0 1 2.12 0Z"
                          />
                        </svg>
                        APP
                      </div>
                      <span className="text-[#949BA4] text-sm font-normal">
                        <span className="mx-1">—</span>
                        {new Date().toLocaleTimeString("en-US", {
                          hour: "numeric",
                          minute: "2-digit",
                          hour12: true,
                        })}
                      </span>
                    </div>
                  </div>

                  {form.content && (
                    <p className="mb-2 text-gray-100 break-words">
                      {replaceVariables(form.content)}
                    </p>
                  )}

                  <div
                    className="border-l-4 relative rounded bg-[#2b2d31]"
                    style={{
                      borderColor: form.color || "#1e40af",
                    }}
                  >
                    <div className="p-4 space-y-2">
                      {form.author?.name && (
                        <div className="flex items-center gap-2">
                          {form.author.icon_url && (
                            <img
                              src={replaceVariables(form.author.icon_url)}
                              alt=""
                              className="w-6 h-6 rounded-full"
                            />
                          )}
                          <Text size="2" className="text-white">
                            {replaceVariables(form.author.name)}
                          </Text>
                        </div>
                      )}

                      {form.title && (
                        <Text
                          as="span"
                          size="4"
                          className="font-semibold text-white block"
                        >
                          {replaceVariables(form.title)}
                        </Text>
                      )}

                      {form.description && (
                        <Text
                          className="text-[#dbdee1] whitespace-pre-wrap"
                          dangerouslySetInnerHTML={{
                            __html: formatDiscordMarkdown(
                              replaceVariables(form.description),
                            ),
                          }}
                        />
                      )}

                      {form.fields.length > 0 && (
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2">
                          {form.fields.map((field, i) => (
                            <div
                              key={i}
                              className={field.inline ? "" : "sm:col-span-2"}
                            >
                              <Text size="2" className="font-medium text-white">
                                {replaceVariables(field.name)}
                              </Text>
                              <Text
                                size="2"
                                className="text-[#dbdee1] whitespace-pre-wrap"
                                dangerouslySetInnerHTML={{
                                  __html: formatDiscordMarkdown(
                                    replaceVariables(field.value),
                                  ),
                                }}
                              />
                            </div>
                          ))}
                        </div>
                      )}

                      {form.image && (
                        <img
                          src={replaceVariables(form.image)}
                          alt=""
                          className="rounded-md max-w-full h-auto mt-2"
                        />
                      )}

                      {form.footer?.text && (
                        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-[#ffffff1a]">
                          {form.footer.icon_url && (
                            <img
                              src={replaceVariables(form.footer.icon_url)}
                              alt=""
                              className="w-5 h-5 rounded-full"
                            />
                          )}
                          <Text size="1" className="text-[#dbdee1]">
                            {replaceVariables(form.footer.text)}
                          </Text>
                        </div>
                      )}
                    </div>
                  </div>

                  {form.buttons.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {form.buttons.map((button, i) => {
                        const getButtonStyle = () => {
                          switch (button.style) {
                            case "red":
                              return "bg-red-500";
                            case "green":
                              return "bg-green-500";
                            case "blue":
                              return "bg-blue-500";
                            default:
                              return "bg-gray-500";
                          }
                        };

                        return (
                          <button
                            key={i}
                            className={`
                              px-4 py-2 rounded text-sm font-medium text-white flex items-center gap-2
                              ${getButtonStyle()}
                              ${button.disabled ? "opacity-50 cursor-not-allowed" : "hover:brightness-110"}
                            `}
                            disabled={button.disabled}
                          >
                            {button.emoji && (
                              <span>{replaceVariables(button.emoji)}</span>
                            )}
                            {replaceVariables(button.label || "Button")}
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                <div className="mt-4 p-4 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 font-mono text-sm">
                  <pre className="whitespace-pre-wrap break-all text-gray-300 overflow-x-auto">
                    {generateCode()}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </Grid>
      </Container>

      <Dialog.Root open={showMarkdownGuide} onOpenChange={setShowMarkdownGuide}>
        <AnimatePresence>
          {showMarkdownGuide && (
            <>
              <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
              <Dialog.Content
                className="!p-0 !overflow-hidden fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[500px]"
                style={{ transform: "translate(-50%, -50%)" }}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30,
                  }}
                  className="glass-panel p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <Dialog.Title className="text-xl font-semibold text-gradient">
                        Discord Markdown Guide
                      </Dialog.Title>
                      <Dialog.Description className="text-sm text-muted-foreground mt-1">
                        You can use these markdown features in content,
                        description, and field values.
                      </Dialog.Description>
                    </div>
                    <Dialog.Close asChild>
                      <button
                        className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                        aria-label="Close"
                      >
                        <Cross2Icon className="w-4 h-4" />
                      </button>
                    </Dialog.Close>
                  </div>

                  <div className="p-4 rounded-lg bg-background/50 backdrop-blur-sm border border-white/10">
                    <pre className="text-sm text-white/90 font-mono whitespace-pre-wrap">
                      {markdownExample}
                    </pre>
                  </div>
                </motion.div>
              </Dialog.Content>
            </>
          )}
        </AnimatePresence>
      </Dialog.Root>

      <Dialog.Root
        open={showVariablesGuide}
        onOpenChange={setShowVariablesGuide}
      >
        <AnimatePresence>
          {showVariablesGuide && (
            <>
              <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
              <Dialog.Content
                className="!p-0 !overflow-hidden fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[500px]"
                style={{ transform: "translate(-50%, -50%)" }}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30,
                  }}
                  className="glass-panel p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <Dialog.Title className="text-xl font-semibold text-gradient">
                        Variables Guide
                      </Dialog.Title>
                      <Dialog.Description className="text-sm text-muted-foreground mt-1">
                        You can use these variables in any text field of your
                        embed
                      </Dialog.Description>
                    </div>
                    <Dialog.Close asChild>
                      <button
                        className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                        aria-label="Close"
                      >
                        <Cross2Icon className="w-4 h-4" />
                      </button>
                    </Dialog.Close>
                  </div>

                  <div className="h-[60vh] overflow-y-auto rounded-lg bg-background/50 backdrop-blur-sm border border-white/10">
                    <div className="p-4 font-mono text-sm">
                      <div className="grid grid-cols-1 gap-4">
                        {Object.entries(variables).map(([key, value]) => (
                          <div key={key} className="space-y-1">
                            <div className="flex items-center gap-2">
                              <span className="text-white/90">{key}</span>
                              <button
                                onClick={() => {
                                  navigator.clipboard.writeText(key);
                                  toast.success("Variable copied to clipboard");
                                }}
                                className="p-1 rounded hover:bg-white/5 transition-colors"
                              >
                                <CopyIcon className="w-3 h-3 text-gray-400" />
                              </button>
                            </div>
                            <Text size="1" className="text-gray-400 block pl-4">
                              Example: {value}
                            </Text>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              </Dialog.Content>
            </>
          )}
        </AnimatePresence>
      </Dialog.Root>

      <Dialog.Root open={showImportDialog} onOpenChange={setShowImportDialog}>
        <AnimatePresence>
          {showImportDialog && (
            <>
              <Dialog.Overlay className="fixed inset-0 bg-black/50 backdrop-blur-sm" />
              <Dialog.Content
                className="!p-0 !overflow-hidden fixed top-[50%] left-[50%] max-h-[85vh] w-[90vw] max-w-[500px]"
                style={{ transform: "translate(-50%, -50%)" }}
              >
                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  exit={{ scale: 0.95, opacity: 0 }}
                  transition={{
                    type: "spring",
                    stiffness: 300,
                    damping: 30,
                  }}
                  className="glass-panel p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <Dialog.Title className="text-xl font-semibold text-gradient">
                        Import Embed
                      </Dialog.Title>
                      <Dialog.Description className="text-sm text-muted-foreground mt-1">
                        Paste your embed code below
                      </Dialog.Description>
                    </div>
                    <Dialog.Close asChild>
                      <button
                        className="p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
                        aria-label="Close"
                      >
                        <Cross2Icon className="w-4 h-4" />
                      </button>
                    </Dialog.Close>
                  </div>

                  <div className="space-y-4">
                    <TextArea
                      value={importText}
                      onChange={(e) => setImportText(e.target.value)}
                      className="w-full min-h-[120px] px-3 py-2 bg-background/50 backdrop-blur-sm rounded-lg border border-white/10 focus:outline-none focus:border-accent text-white resize-y font-mono"
                      placeholder="Paste your embed code here..."
                    />
                    <button
                      onClick={() => {
                        try {
                          if (importText.startsWith("{embed}")) {
                            setForm({
                              content: "",
                              color: "#1e40af",
                              author: { name: "", icon_url: "", url: "" },
                              title: "",
                              url: "",
                              description: "",
                              thumbnail: "",
                              image: "",
                              footer: { text: "", icon_url: "" },
                              fields: [],
                              buttons: [],
                            });

                            const parts = importText
                              .replace("{embed}", "")
                              .split("$v")
                              .map((p) => p.slice(1, -1));
                            parts.forEach((part) => {
                              if (part.startsWith("content:"))
                                setForm((prev) => ({
                                  ...prev,
                                  content: part.slice(8),
                                }));
                              if (part.startsWith("color:"))
                                setForm((prev) => ({
                                  ...prev,
                                  color: part.slice(6),
                                }));
                              if (part.startsWith("title:"))
                                setForm((prev) => ({
                                  ...prev,
                                  title: part.slice(6),
                                }));
                              if (part.startsWith("description:"))
                                setForm((prev) => ({
                                  ...prev,
                                  description: part.slice(12),
                                }));
                              if (part.startsWith("url:"))
                                setForm((prev) => ({
                                  ...prev,
                                  url: part.slice(4),
                                }));
                              if (part.startsWith("thumbnail:"))
                                setForm((prev) => ({
                                  ...prev,
                                  thumbnail: part.slice(10),
                                }));
                              if (part.startsWith("image:"))
                                setForm((prev) => ({
                                  ...prev,
                                  image: part.slice(6),
                                }));

                              if (part.startsWith("author:")) {
                                const [name, icon_url, url] = part
                                  .slice(7)
                                  .split(" && ");
                                setForm((prev) => ({
                                  ...prev,
                                  author: {
                                    name,
                                    icon_url: icon_url || "",
                                    url: url || "",
                                  },
                                }));
                              }

                              if (part.startsWith("footer:")) {
                                const [text, icon_url] = part
                                  .slice(7)
                                  .split(" && ");
                                setForm((prev) => ({
                                  ...prev,
                                  footer: { text, icon_url: icon_url || "" },
                                }));
                              }

                              if (part.startsWith("field:")) {
                                const [name, value, inline] = part
                                  .slice(6)
                                  .split(" && ");
                                setForm((prev) => ({
                                  ...prev,
                                  fields: [
                                    ...prev.fields,
                                    {
                                      name: name || "",
                                      value: value || "",
                                      inline: inline === "true",
                                    },
                                  ],
                                }));
                              }

                              if (part.startsWith("button:")) {
                                const button: any = {};
                                part
                                  .slice(7)
                                  .split(" && ")
                                  .forEach((param) => {
                                    if (param.startsWith("label:"))
                                      button.label = param.slice(6);
                                    if (param.startsWith("url:"))
                                      button.url = param.slice(4);
                                    if (param.startsWith("emoji:"))
                                      button.emoji = param.slice(6);
                                    if (param === "disabled")
                                      button.disabled = true;
                                    if (param.startsWith("style:"))
                                      button.style = param.slice(6);
                                  });
                                setForm((prev) => ({
                                  ...prev,
                                  buttons: [...prev.buttons, button],
                                }));
                              }
                            });

                            setShowImportDialog(false);
                            setImportText("");
                            toast.success("Embed imported successfully");
                          } else {
                            toast.error("Invalid embed code");
                          }
                        } catch (error) {
                          toast.error("Failed to parse embed code");
                        }
                      }}
                      className="flex items-center justify-center gap-2 px-4 py-2.5 w-full rounded-lg bg-background/50 backdrop-blur-sm border border-white/10 text-white hover:bg-background/70 transition-colors"
                    >
                      <FileIcon className="w-4 h-4" />
                      <span className="hidden sm:inline">Import</span>
                    </button>
                  </div>
                </motion.div>
              </Dialog.Content>
            </>
          )}
        </AnimatePresence>
      </Dialog.Root>

      <style jsx global>{`
        @keyframes fade-in {
          from {
            opacity: 0;
            transform: translate(-50%, -48%);
          }
          to {
            opacity: 1;
            transform: translate(-50%, -50%);
          }
        }

        .animate-fade-in {
          animation: fade-in 0.2s ease-out;
        }

        .spoiler {
          background-color: #202225;
          border-radius: 3px;
          color: transparent;
          cursor: pointer;
        }
        .spoiler:hover {
          background-color: rgba(32, 34, 37, 0.1);
          color: #dcddde;
        }
        pre {
          background: #2f3136;
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 4px;
          padding: 0.5rem;
          color: #dcddde;
          font-family: "Consolas", "Courier New", monospace;
        }
        code {
          background: #2f3136;
          border-radius: 3px;
          padding: 0.2em 0.4em;
          font-family: "Consolas", "Courier New", monospace;
        }
        blockquote {
          border-left: 4px solid #4f545c;
          padding-left: 12px;
          margin: 4px 0;
        }
        h1 {
          font-size: 1.5em;
          font-weight: bold;
          margin: 0.5em 0;
        }
        h2 {
          font-size: 1.25em;
          font-weight: bold;
          margin: 0.5em 0;
        }
      `}</style>
    </main>
  );
}

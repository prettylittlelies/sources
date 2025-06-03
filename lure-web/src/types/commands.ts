export interface CommandParameter {
  name: string;
  required: boolean;
}

export interface Command {
  name: string;
  description: string;
  aliases: string[];
  usage: string;
  parameters: CommandParameter[];
  cog: string;
}

export type CommandCategory =
  | "All"
  | "Configuration"
  | "Fun"
  | "Information"
  | "LastFM"
  | "Jishaku"
  | "Developer"
  | "Moderation"
  | "VoiceMaster"
  | "Socials"
  | "Starboard"
  | "Music"
  | "Roleplay"
  | "AutoPFP"
  | "Economy"
  | "Utility"
  | "Vanity";

export type CategoryMetadata = {
  name: CommandCategory;
  icon: React.ReactNode;
  commandCount?: number;
};

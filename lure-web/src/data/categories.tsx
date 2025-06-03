import { CategoryMetadata } from "@/types/commands";
import {
  LayersIcon,
  GearIcon,
  RocketIcon,
  InfoCircledIcon,
  HeartIcon,
  LockClosedIcon,
  SpeakerLoudIcon,
  Share2Icon,
  StarIcon,
  FaceIcon,
  PlayIcon,
  ImageIcon,
  BarChartIcon,
  Pencil1Icon,
  ChatBubbleIcon
} from "@radix-ui/react-icons";

export const categories: CategoryMetadata[] = [
  {
    name: "All",
    icon: <LayersIcon className="w-4 h-4" />,
  },
  {
    name: "AutoPFP",
    icon: <ImageIcon className="w-4 h-4" />,
  },
  {
    name: "Configuration",
    icon: <GearIcon className="w-4 h-4" />,
  },
  {
    name: "Economy",
    icon: <BarChartIcon className="w-4 h-4" />,
  },
  {
    name: "Fun",
    icon: <RocketIcon className="w-4 h-4" />,
  },
  {
    name: "Information",
    icon: <InfoCircledIcon className="w-4 h-4" />,
  },
  {
    name: "LastFM",
    icon: <HeartIcon className="w-4 h-4" />,
  },
  {
    name: "Moderation",
    icon: <LockClosedIcon className="w-4 h-4" />,
  },
  {
    name: "Music",
    icon: <PlayIcon className="w-4 h-4" />,
  },
  {
    name: "Roleplay",
    icon: <FaceIcon className="w-4 h-4" />,
  },
  {
    name: "Socials",
    icon: <Share2Icon className="w-4 h-4" />,
  },
  {
    name: "Starboard",
    icon: <StarIcon className="w-4 h-4" />,
  },
  {
    name: "VoiceMaster",
    icon: <SpeakerLoudIcon className="w-4 h-4" />,
  },
  {
    name: "Utility",
    icon: <Pencil1Icon className="w-4 h-4" />,
  },
  {
    name: "Vanity",
    icon: <ChatBubbleIcon className="w-4 h-4" />,
  },
];

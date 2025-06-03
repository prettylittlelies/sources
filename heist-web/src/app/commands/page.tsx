"use client"

import { useState } from 'react'
// import Navbar from '@/components/navbar'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import commandsData from '@/data/commands.json'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Layout, 
  MessageCircle, 
  Share2, 
  Heart, 
  Wallet, 
  Sparkles, 
  Gamepad2, 
  Settings as SettingsIcon, 
  Info, 
  Wrench,
  Search
} from 'lucide-react'

interface BaseCommand {
  name: string;
  description: string;
  usage: string;
  category: string;
  premium?: boolean;
  example?: string;
  subcommands?: BaseCommand[];
}

interface CommandsData {
  [key: string]: BaseCommand;
}

const categoryIcons: { [key: string]: React.ReactNode } = {
  'All': <Layout className="w-4 h-4" />,
  'Discord': <MessageCircle className="w-4 h-4" />,
  'Socials': <Share2 className="w-4 h-4" />,
  'Reactions': <Heart className="w-4 h-4" />,
  'Economy': <Wallet className="w-4 h-4" />,
  'Fun': <Sparkles className="w-4 h-4" />,
  'Games': <Gamepad2 className="w-4 h-4" />,
  'Settings': <SettingsIcon className="w-4 h-4" />,
  'Info': <Info className="w-4 h-4" />,
  'Utility': <Wrench className="w-4 h-4" />
}

export default function Features() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')

  const getAllCommands = () => {
    const commands: BaseCommand[] = []
    
    Object.values(commandsData as CommandsData).forEach((command) => {
      if (command.category === 'Owner') return;

      if (command.usage === "Group") {
        if (command.subcommands) {
          command.subcommands.forEach(subCommand => {
            if (subCommand.usage === "Group" && subCommand.subcommands) {
              subCommand.subcommands.forEach(nestedCommand => {
                commands.push({
                  ...nestedCommand,
                  name: `${command.name} ${subCommand.name} ${nestedCommand.name}`
                })
              })
            } else {
              commands.push({
                ...subCommand,
                name: `${command.name} ${subCommand.name}`
              })
            }
          })
        }
      } else {
        commands.push(command)
      }
    })
    return commands
  }

  const allCommands = getAllCommands()
  const categories = ['All', ...new Set(allCommands.map(command => command.category))].filter(cat => cat !== 'Owner')

  const filteredCommands = allCommands.filter(command => 
    command.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (selectedCategory === 'All' || command.category === selectedCategory)
  )

  const cardVariants = {
    initial: { 
      opacity: 0,
      scale: 0.98
    },
    animate: { 
      opacity: 1,
      scale: 1
    },
    exit: {
      opacity: 0,
      scale: 0.98
    }
  }

  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-8 md:py-16">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 text-center">
          Commands
          <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text"> Overview</span>
        </h1>
        
        <div className="space-y-4 md:space-y-6 mb-8">
          <div className="flex justify-center">
            <div className="relative w-full max-w-sm">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40 z-10" />
              <Input
                type="text"
                placeholder="Search commands..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] text-white/90 placeholder:text-white/40"
              />
            </div>
          </div>
          
          <div className="flex flex-wrap justify-center gap-2 px-2">
            <div className="inline-flex flex-wrap justify-center gap-2 max-w-full overflow-x-auto pb-2 px-4 -mx-2">
              {categories.map(category => (
                <Button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`whitespace-nowrap text-sm inline-flex items-center gap-2
                    ${selectedCategory === category
                      ? "bg-gradient-to-b from-white/[0.04] to-transparent backdrop-blur-sm border border-white/[0.03] text-white/90 hover:bg-white/[0.06] shadow-none rounded-full px-4 py-2"
                      : "bg-gradient-to-b from-white/[0.02] to-transparent backdrop-blur-sm border border-white/[0.02] text-white/40 hover:bg-white/[0.04] shadow-none rounded-full px-4 py-2"
                    }
                  `}
                >
                  {categoryIcons[category]}
                  {category}
                </Button>
              ))}
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">
          <AnimatePresence initial={false}>
            {filteredCommands.map((command) => (
              <motion.div
                key={command.name}
                variants={cardVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={{
                  duration: 0.2,
                  ease: "easeInOut"
                }}
                style={{ height: '100%' }}
              >
                <Card className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] h-full flex flex-col">
                  <CardHeader className="flex-none">
                    <CardTitle className="flex justify-between items-center">
                      <span className="text-white/90 font-normal truncate mr-2">{command.name}</span>
                      {command.premium && (
                        <Badge className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] text-white/60 rounded-full px-4 font-light flex-none">
                          Premium
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription className="text-white/40 line-clamp-2">{command.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="text-white/60 flex-grow">
                    <div className="space-y-2">
                      <p><span className="text-white/40">Usage:</span> <span className="break-words">{command.usage}</span></p>
                      {command.example && (
                        <p><span className="text-white/40">Example:</span> <span className="break-words">{command.example}</span></p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </main>
    </div>
  )
}


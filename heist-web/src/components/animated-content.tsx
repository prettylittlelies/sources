'use client'

import { motion } from 'framer-motion'
import { Badge } from '@/components/ui/badge'
import { Instagram, Music2, Sparkles } from 'lucide-react'

export function AnimatedHeading() {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      Heist is Discord's
      <br />
      ultimate <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text">all-in-one</span> bot
    </motion.div>
  )
}

export function AnimatedDescription() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
    >
      A versatile multipurpose bot designed to elevate your Discord server with powerful features and intuitive user-focused commands.
    </motion.div>
  )
}

export function AnimatedStats({ userCount, guildCount }: { userCount: number; guildCount: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.6 }}
    >
      serving <span className="text-white font-medium">{userCount.toLocaleString()}+</span> users and{' '}
      <span className="text-white font-medium">{guildCount.toLocaleString()}+</span> guilds
    </motion.div>
  )
}

export function AnimatedFeatures() {
  const features = [
    { icon: <Instagram className="w-3 h-3 text-white/40" />, text: "social media" },
    { icon: <Music2 className="w-3 h-3 text-white/40" />, text: "lastfm integration" },
    { icon: <Sparkles className="w-3 h-3 text-white/40" />, text: "ai tools" }
  ];

  return (
    <>
      {features.map((feature, index) => (
        <motion.div
          key={feature.text}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.9 + (index * 0.1) }}
        >
          <Badge className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] px-3 sm:px-6 py-2 sm:py-3 font-mono text-xs sm:text-sm flex items-center gap-1 sm:gap-2 hover:bg-white/[0.06] transition-all shadow-none">
            <div className="aspect-square w-4 sm:w-5 rounded-full bg-white/[0.02] flex items-center justify-center backdrop-blur-sm">
              {feature.icon}
            </div>
            {feature.text}
          </Badge>
        </motion.div>
      ))}
    </>
  )
}

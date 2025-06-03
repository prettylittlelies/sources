import { Button } from "@/components/ui/button"
import { Plus, ArrowRight, MoonStar } from 'lucide-react'
import Link from 'next/link'
import { AnimatedHeading, AnimatedDescription, AnimatedStats, AnimatedFeatures } from '@/components/animated-content'

export default async function Home() {
  const res = await fetch('https://api.csyn.me/getcount', {
    next: { revalidate: 60 }
  });
  const stats = await res.json();

  return (
    <div className="text-center space-y-4 max-w-4xl mx-auto">
      <div className="text-6xl md:text-7xl font-bold tracking-tight text-white">
        <AnimatedHeading />
      </div>
      
      <div className="text-lg text-white/60 max-w-2xl mx-auto">
        <AnimatedDescription />
      </div>

      <div className="text-white/60 font-mono text-base py-2">
        <AnimatedStats 
          userCount={stats.discord_user_install_count}
          guildCount={stats.discord_guild_count}
        />
      </div>

      <div className="flex justify-center space-x-2 sm:space-x-4 py-8 overflow-hidden px-2 sm:px-4">
        <AnimatedFeatures />
      </div>

      <div className="flex justify-center gap-4 pt-4">
        <Button asChild className="bg-gradient-to-b from-white/[0.04] to-transparent text-white/90 rounded-full h-12 px-6 border border-white/[0.03] backdrop-blur-sm shadow-none hover:bg-white/[0.06] transition-all duration-300">
          <Link href="https://discord.com/oauth2/authorize?client_id=1225070865935368265">
            <Plus className="mr-2 h-5 w-5 opacity-60" />
            Add to Discord
          </Link>
        </Button>
        <Button asChild className="bg-gradient-to-b from-white/[0.03] to-transparent rounded-full h-12 px-6 border border-white/[0.02] hover:bg-white/[0.05] backdrop-blur-sm shadow-none transition-all duration-300">
          <Link href="/premium">
            <MoonStar className="ml-2 h-5 w-5 opacity-60" />
            Premium
            <ArrowRight className="ml-2 h-5 w-5 opacity-60" />
          </Link>
        </Button>
      </div>
    </div>
  )
}


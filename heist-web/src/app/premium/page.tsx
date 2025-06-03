import Navbar from '@/components/navbar'
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Check, Link2, Star, X } from 'lucide-react'

export default function Premium() {
  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-8 md:py-16">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 text-center">
          Heist
          <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text"> Premium</span>
        </h1>
        
        <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-12">
          <Card className="bg-gradient-to-b from-white/[0.02] to-transparent backdrop-blur-sm border border-white/[0.02]">
            <CardHeader className="space-y-2">
              <CardTitle className="text-2xl text-white/60 font-normal">Free Plan</CardTitle>
              <CardDescription className="text-white/40">Start your journey with Heist</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {[
                  { text: 'All free features', positive: true },
                  { text: 'Cooldowns & limits', positive: false },
                  { text: 'Special badge', positive: false },
                  { text: 'Default embed color', positive: false },
                  { text: 'Standard economy luck', positive: false }
                ].map((feature, index) => (
                  <li key={index} className="flex items-center text-white/40">
                    <div className={`w-5 h-5 rounded-full ${feature.positive ? 'bg-white/[0.02]' : 'bg-white/[0.01]'} flex items-center justify-center backdrop-blur-sm mr-3`}>
                      {feature.positive ? (
                        <Check className="w-3 h-3 text-white/20" />
                      ) : (
                        <X className="w-3 h-3 text-white/10" />
                      )}
                    </div>
                    {feature.text}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
                <Button asChild className="w-full bg-gradient-to-b from-white/[0.03] to-transparent text-white/60 rounded-full h-12 px-6 border border-white/[0.02] backdrop-blur-sm shadow-none hover:bg-white/[0.04] transition-all duration-300">
                <a href="https://discord.com/oauth2/authorize?client_id=1225070865935368265" target="_blank">
                  <Link2 className="mr-2 h-4 w-4 opacity-60" />
                  Authorize Bot
                </a>
                </Button>
            </CardFooter>
          </Card>

          <Card className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] relative overflow-hidden">
            <div className="absolute top-0 right-0 px-3 py-1 bg-gradient-to-b from-white/[0.06] to-transparent backdrop-blur-sm border-l border-b border-white/[0.03] rounded-bl-lg text-white/60 text-sm">
              Recommended
            </div>
            <CardHeader className="space-y-2">
              <CardTitle className="text-2xl text-white/90 font-normal">Premium Plan</CardTitle>
              <CardDescription className="text-white/40">Unlock the full potential</CardDescription>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {[
                  'All free & premium features',
                  'No cooldowns & limits',
                  'Special badge',
                  'Custom embed color',
                  'Increased economy luck'
                ].map((feature, index) => (
                  <li key={index} className="flex items-center text-white/60">
                    <div className="w-5 h-5 rounded-full bg-white/[0.02] flex items-center justify-center backdrop-blur-sm mr-3">
                      <Check className="w-3 h-3 text-white/40" />
                    </div>
                    {feature}
                  </li>
                ))}
              </ul>
            </CardContent>
            <CardFooter>
              <Button asChild className="w-full bg-gradient-to-b from-white/[0.04] to-transparent text-white/90 rounded-full h-12 px-6 border border-white/[0.03] backdrop-blur-sm shadow-none hover:bg-white/[0.06] transition-all duration-300">
              <a href="https://discord.gg/heistbot" target="_blank">
                <Star className="mr-2 h-4 w-4 opacity-60" />
                Upgrade to Premium
              </a>
              </Button>
            </CardFooter>
          </Card>
        </div>
      </main>
    </div>
  )
}


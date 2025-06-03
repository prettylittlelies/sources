import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function Terms() {
  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-8 md:py-16">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 text-center">
          Terms of
          <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text"> Service</span>
        </h1>

        <Card className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl text-white/90 font-normal">Terms of Service</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-white/60">
            <p>
              Terms of service for the Heist bot, this guides our users on proper usage of the bot.
            </p>

            <div>
              <h3 className="text-lg text-white/80 mb-2">Conditions</h3>
              <p>
                Our terms and conditions apply to each and every user of Heist Bot.
                By adding Heist in your server or authorizing it as an User App, you agree to these terms of service 
                and the future terms which we may add after a notice.
              </p>
            </div>

            <div>
              <h3 className="text-lg text-white/80 mb-2">Terms of Use</h3>
              <ul className="list-disc pl-6 space-y-2">
                <li>Intentional command spam or attempts to crash the bot should not be made.</li>
                <li>Heist should not be used in bot spam servers which cause command spam.</li>
                <li>Heist Team reserves the rights to prohibit any server or user from using Heist.</li>
                <li>The user is responsible for any violation caused by them.</li>
                <li>We have the rights to update terms of service anytime with a notice in the support server.</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

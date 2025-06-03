import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export default function Privacy() {
  return (
    <div className="min-h-screen">
      <main className="container mx-auto px-4 py-8 md:py-16">
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white mb-8 text-center">
          Privacy
          <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text"> Policy</span>
        </h1>

        <Card className="bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm border border-white/[0.03] max-w-4xl mx-auto">
          <CardHeader>
            <CardTitle className="text-2xl text-white/90 font-normal">Privacy Policy</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6 text-white/60">
            <p>
              This Privacy Policy explains how information is collected, used, and disclosed by the Heist bot.
            </p>

            <div>
              <h3 className="text-lg text-white/80 mb-2">Information Collection and Use</h3>
              <p>
                We collect certain information about users of the Heist bot, including but not limited to user IDs, 
                server IDs, and usage data. This information is used to provide and improve the service, as well as 
                to monitor and analyze usage patterns.
              </p>
            </div>

            <div>
              <h3 className="text-lg text-white/80 mb-2">Information Sharing and Disclosure</h3>
              <p>
                We do not share or disclose any personal information collected through the Heist bot, except as 
                described in this Privacy Policy or with user consent. Aggregate, anonymized data may be shared 
                for analytical purposes or to improve the service.
              </p>
            </div>

            <div>
              <h3 className="text-lg text-white/80 mb-2">Changes to This Privacy Policy</h3>
              <p>
                We reserve the right to update or change this Privacy Policy at any time. Any changes will be 
                effective immediately upon posting the updated Privacy Policy on the Heist support server.
              </p>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  )
}

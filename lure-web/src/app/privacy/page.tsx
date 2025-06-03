export default function PrivacyPage() {
  return (
    <main className="min-h-screen pt-24 pb-16 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-gradient mb-2">
            Privacy Policy
          </h1>
          <p className="text-muted-foreground">
            Last updated and effective: March 14, 2025, 8:30 PM GMT
          </p>
        </div>

        <div className="glass-panel backdrop-blur-sm bg-background/50 p-6 space-y-8">
          <p className="italic text-white/80 border-l-2 border-[#8faaa2]/30 pl-4 py-1">
            Any information we collect is not used maliciously. If any
            information stated here seems/is misleading, please contact us
            immediately through our support server.
          </p>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Information We Collect
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <ul className="list-disc list-inside space-y-1.5 marker:text-[#8faaa2]/70">
                <li>Guild IDs</li>
                <li>Guild Names</li>
                <li>Channel IDs</li>
                <li>Role IDs</li>
                <li>User IDs</li>
                <li>Message Timestamps</li>
              </ul>
              <ul className="list-disc list-inside space-y-1.5 marker:text-[#8faaa2]/70">
                <li>Message IDs</li>
                <li>Nicknames and Usernames</li>
                <li className="text-pretty">
                  Message Content when a command is ran (stored for a max of 14
                  days)
                </li>
                <li className="text-pretty">
                  Last deleted message content (stored for a max of 2 hours or
                  less, 19 entries allowed)
                </li>
                <li className="text-pretty">
                  Last message edit history (stored for a max of 2 hours or
                  less, 19 entries allowed)
                </li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Why do you need the data and how is it used?
            </h2>
            <div className="space-y-4">
              <p className="text-white/90 leading-relaxed">
                When a command is invoked, we store that message content for a
                maximum of 14 days for debugging purposes. We also store a
                maximum of 18 entries for edited messages and sniping messages
                that will expire in two hours or less in volatile memory.
              </p>
              <div className="pl-4 border-l-2 border-[#8faaa2]/20 space-y-3">
                <p className="text-white/90 leading-relaxed">
                  Guild IDs, Channel IDs, Role IDs, User IDs and Message IDs are
                  all stored for our system to aggregate values to find data.
                </p>
                <p className="text-white/90 leading-relaxed">
                  Nickname and Username changes are logged in order for the
                  "namehistory" command to function. Users can clear this data
                  themselves at any time.
                </p>
                <p className="text-white/90 leading-relaxed">
                  Guild name changes are logged in order for the "gnames"
                  command to function. Server administrators can clear this data
                  themselves at any time.
                </p>
              </div>
            </div>
          </section>

          <section className="bg-[#8faaa2]/5 p-4 rounded-lg backdrop-blur-sm border border-[#8faaa2]/10">
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Who is your collected information shared with?
            </h2>
            <p className="text-white/90 font-medium">
              We do not sell and expose your information to others/third parties
              by any means.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Data removal
            </h2>
            <p className="text-white/90 leading-relaxed">
              Contact us through our support server to have your data deleted.
            </p>
            <div className="mt-2 p-3 border border-[#8faaa2]/10 rounded-lg bg-[#8faaa2]/5 backdrop-blur-sm">
              <p className="text-sm text-white/70">
                Note: When requesting deletion, please be specific with what
                information that you want gone and provide ownership of your
                Discord account. Response time may vary and could take up to two
                weeks.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Request data
            </h2>
            <p className="text-white/90 leading-relaxed">
              Contact us through our support server for all of your data that we
              are currently storing. Response time may vary and could take up to
              7 days.
            </p>
          </section>

          <section className="bg-[#8faaa2]/5 p-4 rounded-lg backdrop-blur-sm border border-[#8faaa2]/10">
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Changes to the Privacy Policy
            </h2>
            <p className="text-white/90 leading-relaxed">
              We can update these terms at any time without notice. Continuing
              to use our services after any changes will mean that you agree
              with these terms and violation of our terms of service could
              result in a permanent ban across all of our services.
            </p>
          </section>
        </div>
      </div>
    </main>
  );
}

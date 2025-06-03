export default function TermsPage() {
  return (
    <main className="min-h-screen pt-24 pb-16 px-4">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-medium text-gradient mb-2">
            Terms of Service
          </h1>
          <p className="text-muted-foreground">
            Last updated and effective: March 14, 2025, 8:30 PM GMT
          </p>
        </div>

        <div className="glass-panel backdrop-blur-sm bg-background/50 p-6 space-y-8">
          <p className="text-white/90 leading-relaxed">
            By visiting ("Tempt") or inviting ("Tempt Bot") to your Discord server
            or logging into our website, you agree and consent to the terms
            displayed on this page including our policies (Privacy Policy). When
            we state "Tempt," "we," "us," and "our" in these terms, we mean Tempt.
            "Services" mean Tempt's services that we offer to users.
          </p>

          <p className="italic text-white/80 border-l-2 border-[#8faaa2]/30 pl-4 py-1">
            If any information stated here seems/is misleading, please contact
            us immediately through our support server.
          </p>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Disclaimer
            </h2>
            <p className="text-white/90 leading-relaxed">
              You may not use Tempt to violate any applicable laws or regulations
              as well as Discord's Terms of Service and Community Guidelines. If
              you encounter individuals or communities doing so, please contact
              us through our support server. If you are refunded under any
              circumstances, your Discord account may be subject to blacklist
              and a ban from all of our services.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Website Usage
            </h2>
            <p className="text-white/90 leading-relaxed mb-3">
              You are required to be compliant with the terms shown on this
              page. You are not to do any of the following:
            </p>
            <ul className="list-disc list-inside space-y-1.5 marker:text-[#8faaa2]/70 text-white/90">
              <li>Malicious attempts of exploiting the website</li>
              <li>Malicious use of the website</li>
              <li>Scraping content on this website for malicious use</li>
              <li>Framing a portion or all of the website</li>
              <li>
                Plagiarize Tempt's website and claiming it as your own work
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Bot Usage
            </h2>
            <p className="text-white/90 leading-relaxed mb-3">
              You are not to do any of the following:
            </p>
            <ul className="list-disc list-inside space-y-1.5 marker:text-[#8faaa2]/70 text-white/90">
              <li>Violate the Discord Terms of Service</li>
              <li>Plagiarize Tempt's services or features</li>
              <li>Assist anyone in plagiarizing Tempt's services or features</li>
              <li>Abuse or exploit Tempt or any of our services</li>
              <li>Run a Discord Server that has been terminated repeatedly</li>
              <li>
                Organize any "raid" or witch-hunt on Tempt itself or its staff
              </li>
            </ul>
          </section>

          <section className="bg-[#8faaa2]/5 p-4 rounded-lg backdrop-blur-sm border border-[#8faaa2]/10">
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Termination
            </h2>
            <p className="text-white/90 leading-relaxed">
              We reserve the right to terminate your access to our services
              immediately (under our sole discretion) without prior notice or
              liability for any reason (including, but not limited to, a breach
              of the terms).
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Indemnity
            </h2>
            <p className="text-white/90 leading-relaxed">
              You shall indemnify us against all liabilities, costs, expenses,
              damages and losses (including any direct, indirect or
              consequential losses, loss of profit, loss of reputation and all
              interest, penalties and legal and other reasonable professional
              costs and expenses) suffered or incurred by you arising out of or
              in connection with your use of the service, or a breach of the
              terms.
            </p>
          </section>

          <section className="bg-[#8faaa2]/5 p-4 rounded-lg backdrop-blur-sm border border-[#8faaa2]/10">
            <h2 className="text-2xl font-medium mb-4 text-gradient">
              Changes to the Terms of Service
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

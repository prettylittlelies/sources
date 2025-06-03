import Link from 'next/link'
import { ExternalLink } from 'lucide-react'

export default function Footer() {
  return (
    <footer className="w-full py-4 px-4 bg-black/50 backdrop-blur-sm">
      <div className="container mx-auto flex flex-col md:flex-row justify-between items-center text-sm text-gray-400 gap-4 md:gap-0">
        <div className="flex flex-col md:flex-row items-center gap-1 text-center">
          <div>© 2024 Heist Bot</div>
          <div className="flex items-center gap-1">
            <span className="hidden md:inline">by</span>
            <span className="md:hidden">Made by</span>
            <Link href="https://csyn.me" target="_blank" rel="referrer" className="hover:text-white transition-colors flex items-center gap-1">
              cosmin
              <ExternalLink size={14} />
            </Link>
            &
            <Link href="https://bhop.rest" target="_blank" rel="referrer" className="hover:text-white transition-colors flex items-center gap-1">
              bhop
              <ExternalLink size={14} />
            </Link>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/faq" className="hover:text-white transition-colors">
            FAQ
          </Link>
          <Link href="/privacy" className="hover:text-white transition-colors">
            Privacy
          </Link>
          <Link href="/terms" className="hover:text-white transition-colors">
            Terms
          </Link>
        </div>
      </div>
    </footer>
  )
}

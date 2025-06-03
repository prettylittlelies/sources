"use client"
import Link from 'next/link'
import { Button } from "@/components/ui/button"
import Image from 'next/image'
import { useState } from 'react'
import { Menu, X } from 'lucide-react'

export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] md:w-auto">
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-full flex items-center justify-between md:justify-start">
        <div className="flex items-center">
          <Link href="/" className="flex items-center px-3 py-2">
            <Image
              src="https://csyn.me/assets/heist.png"
              alt="Heist"
              width={28}
              height={28}
              className="rounded-full"
            />
          </Link>
          <div className="w-[1px] h-4 bg-white/10" />

          <div className="hidden md:flex items-center">
            <Link href="/commands" className="text-sm text-gray-300 px-4 py-2 transition-colors duration-200 hover:text-white">
              Commands
            </Link>
            <div className="w-[1px] h-4 bg-white/10" />
            <Link href="/faq" className="text-sm text-gray-300 px-4 py-2 transition-colors duration-200 hover:text-white">
              FAQ
            </Link>
            <div className="w-[1px] h-4 bg-white/10" />
            <Link href="/premium" className="text-sm text-gray-300 px-4 py-2 transition-colors duration-200 hover:text-white">
              Premium
            </Link>
            <div className="w-[1px] h-4 bg-white/10" />
            <Link href="https://discord.gg/heistbot" className="text-sm text-gray-300 px-4 py-2 transition-colors duration-200 hover:text-white">
              Discord
            </Link>
          </div>
        </div>

        <button
          className="md:hidden px-3 py-2"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      <div className={`md:hidden absolute top-full left-0 right-0 mt-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-xl overflow-hidden transition-all duration-200 ${
        mobileMenuOpen ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'
      }`}>
        <div className="flex flex-col divide-y divide-white/10">
          <Link href="/commands" className="text-sm text-gray-300 px-4 py-3 hover:bg-white/5 transition-colors duration-200">
            Commands
          </Link>
          <Link href="/faq" className="text-sm text-gray-300 px-4 py-3 hover:bg-white/5 transition-colors duration-200">
            FAQ
          </Link>
          <Link href="/premium" className="text-sm text-gray-300 px-4 py-3 hover:bg-white/5 transition-colors duration-200">
            Premium
          </Link>
          <Link href="https://discord.gg/heistbot" className="text-sm text-gray-300 px-4 py-3 hover:bg-white/5 transition-colors duration-200">
            Discord
          </Link>
        </div>
      </div>
    </nav>
  )
}


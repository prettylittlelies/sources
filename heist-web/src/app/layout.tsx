import type { Metadata } from 'next'
import { Poppins } from 'next/font/google'
import './globals.css'
import Navbar from '@/components/navbar'
import Footer from '@/components/footer'

const poppins = Poppins({ 
  subsets: ['latin'],
  weight: ['400'],
  display: 'swap'
})

export const metadata: Metadata = {
  title: 'Heist Discord Bot',
  description: 'A multipurpose all-in-one bot, enhancing your experience with user-focused commands.',
}

// تشاسي تنشيسا تشي تاتشسي تىشتاسي 😭☠️

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={poppins.className}>
        <div className="min-h-screen bg-black overflow-hidden relative flex flex-col">
          <div className="absolute inset-0 bg-gradient-to-b bg-white/3 to-black pointer-events-none" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-gray-900/40 via-black to-black pointer-events-none" />
          
          <div className="absolute inset-0 pointer-events-none">
            <svg className="w-full h-full opacity-35">
              <defs>
                <pattern id="stars1" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                  <circle cx="50" cy="50" r="0.8" fill="white" opacity="0.4">
                    <animate attributeName="opacity" values="0.2;0.4;0.2" dur="4s" repeatCount="indefinite" />
                  </circle>
                  <circle cx="20" cy="80" r="0.5" fill="white" opacity="0.3" />
                  <animateTransform
                    attributeName="patternTransform"
                    attributeType="XML"
                    type="translate"
                    from="0 0"
                    to="100 100"
                    dur="20s"
                    repeatCount="indefinite"
                  />
                </pattern>
                <pattern id="stars2" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
                  <circle cx="70" cy="30" r="0.6" fill="white" opacity="0.3">
                    <animate attributeName="opacity" values="0.3;0.1;0.3" dur="5s" repeatCount="indefinite" />
                  </circle>
                  <animateTransform
                    attributeName="patternTransform"
                    attributeType="XML"
                    type="translate"
                    from="0 0"
                    to="-100 -100"
                    dur="25s"
                    repeatCount="indefinite"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#stars1)" />
              <rect width="100%" height="100%" fill="url(#stars2)" />
            </svg>
          </div>

          <Navbar />
          
          <main className="container relative mx-auto px-4 pt-32 pb-24 flex-grow">
            {children}
          </main>

          <Footer />
        </div>
      </body>
    </html>
  )
}

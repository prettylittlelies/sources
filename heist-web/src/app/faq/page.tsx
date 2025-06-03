'use client'
import { motion } from 'framer-motion'
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

const faqs = [
    {
        question: "What is Heist bot?",
        answer: "Heist is a multipurpose Discord bot that combines social features, music integration, AI tools, and server management into one seamless experience."
    },
    {
        question: "Is Heist bot free to use?",
        answer: "Yes! Heist offers a free tier with access to core features. Premium features are available through our Premium plan for enhanced functionality."
    },
    {
        question: "How do I add Heist to my server?",
        answer: "You can either authorize Heist as a user application or add it directly to your server. Simply click the 'Add to Discord' button on the homepage to get started."
    },
    {
        question: "What makes Heist different from other bots?",
        answer: "Heist combines multiple bot functionalities into one, reducing clutter in your server. We focus on user experience and regular feature updates."
    },
    {
        question: "Do you have a support server?",
        answer: "Yes! Join our Discord community for support, feature requests, and updates. Just click the 'Discord' button in the navigation bar to join our server."
    }
]

export default function FAQ() {
  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-12">
        <div className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-4">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Frequently Asked
            <span className="bg-gradient-to-r from-white/60 to-white/80 text-transparent bg-clip-text"> Questions</span>
          </motion.div>
        </div>
        <div className="text-white/60">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Find answers to common questions about Heist bot
          </motion.div>
        </div>
      </div>

      <Accordion type="single" collapsible className="space-y-4">
        {faqs.map((faq, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
          >
            <AccordionItem value={`item-${index}`} className="border border-white/[0.03] bg-gradient-to-b from-white/[0.03] to-transparent backdrop-blur-sm rounded-lg px-4">
              <AccordionTrigger className="text-white/80 hover:text-white/90 text-left">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-white/60">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          </motion.div>
        ))}
      </Accordion>
    </div>
  )
}

'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ShieldAlert, 
  Search, 
  ChevronDown, 
  HelpCircle, 
  BookOpen, 
  Mail, 
  MessageSquare,
  AlertTriangle,
  Zap,
  CheckCircle2,
  FileText
} from 'lucide-react'

export default function HelpCenter() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeFaq, setActiveFaq] = useState<number | null>(null)

  const faqs = [
    {
      question: "How does the deepfake detection mechanism work?",
      answer: "Our system uses a 6-layer defense mechanism analyzing acoustics, speaker identity consistency, prosody, paralinguistics, semantics, and cryptographic watermarks to determine authenticity."
    },
    {
      question: "What happens if a watermark is found?",
      answer: "If a cryptographic watermark is detected, the audio is immediately flagged as synthetic (Deepfake) regardless of how authentic it sounds, as the watermark is an undeniable signature of our generative engine."
    },
    {
      question: "How do I revoke a compromised API key?",
      answer: "Navigate to your Profile Settings > API Access. Click 'Revoke Key' and immediately generate a new one. All active sessions using the old key will be terminated."
    },
    {
      question: "Are my analysis results stored permanently?",
      answer: "No. Analysis data is processed in memory and forensic reports are stored temporarily for 24 hours unless you explicitly save them to your account dashboard."
    }
  ]

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text-1)] font-sans pb-24">
      {/* Hero Section */}
      <section className="pt-24 pb-16 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-[var(--surface-1)] to-[var(--bg)] -z-10" />
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[var(--accent-bg)] border border-[var(--accent-border)] mb-8">
            <HelpCircle className="w-4 h-4 text-[var(--accent)]" />
            <span className="text-xs font-medium text-[var(--accent)] tracking-wider uppercase">Support Center</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">How can we help you?</h1>
          
          <div className="relative max-w-2xl mx-auto mt-10">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-[var(--text-3)]" />
            <input 
              type="text" 
              placeholder="Search documentation, FAQs, or security advisories..." 
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="w-full bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl py-4 pl-12 pr-6 text-[var(--text-1)] placeholder-[var(--text-3)] focus:outline-none focus:border-[var(--accent)] focus:ring-1 focus:ring-[var(--accent)] transition-all shadow-lg"
            />
          </div>
        </div>
      </section>

      <div className="max-w-5xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
        {/* Quick Links */}
        <div className="space-y-4">
          <h3 className="text-lg font-semibold mb-6 px-2">Resources</h3>
          
          <ResourceCard 
            icon={BookOpen} 
            title="Documentation" 
            desc="API references and integration guides."
          />
          <ResourceCard 
            icon={ShieldAlert} 
            title="Security Center" 
            desc="Report vulnerabilities or deepfake abuse."
          />
          <ResourceCard 
            icon={MessageSquare} 
            title="Community Forum" 
            desc="Discuss use cases with other developers."
          />
        </div>

        {/* FAQs */}
        <div className="md:col-span-2 space-y-6">
          <h3 className="text-lg font-semibold mb-6">Frequently Asked Questions</h3>
          
          <div className="space-y-3">
            {faqs.map((faq, idx) => (
              <div 
                key={idx} 
                className="bg-[var(--surface-1)] border border-[var(--border)] rounded-xl overflow-hidden transition-colors hover:border-[var(--border-strong)]"
              >
                <button 
                  onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                  className="w-full px-6 py-4 flex items-center justify-between text-left focus:outline-none"
                >
                  <span className="font-medium">{faq.question}</span>
                  <ChevronDown className={`w-5 h-5 text-[var(--text-3)] transition-transform ${activeFaq === idx ? 'rotate-180' : ''}`} />
                </button>
                <AnimatePresence>
                  {activeFaq === idx && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="px-6 pb-5 text-[var(--text-2)] text-sm leading-relaxed"
                    >
                      {faq.answer}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>

          {/* Contact Support Form */}
          <div className="mt-12 bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl p-8 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-8 opacity-5">
              <Mail className="w-32 h-32" />
            </div>
            
            <h3 className="text-xl font-bold mb-2">Still need help?</h3>
            <p className="text-[var(--text-2)] text-sm mb-8 max-w-md">
              Create a support ticket and our security engineers will get back to you within 24 hours.
            </p>

            <form className="space-y-5 relative z-10" onSubmit={(e) => e.preventDefault()}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="space-y-2">
                  <label className="text-xs font-medium text-[var(--text-2)] ml-1">Email Address</label>
                  <input type="email" className="w-full bg-[var(--surface-2)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--accent)]" placeholder="you@company.com" />
                </div>
                <div className="space-y-2">
                  <label className="text-xs font-medium text-[var(--text-2)] ml-1">Topic</label>
                  <select className="w-full bg-[var(--surface-2)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--accent)] appearance-none text-[var(--text-1)]">
                    <option>Technical Integration</option>
                    <option>Billing & Licensing</option>
                    <option>Report Deepfake Abuse</option>
                    <option>Other</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-medium text-[var(--text-2)] ml-1">Message</label>
                <textarea rows={4} className="w-full bg-[var(--surface-2)] border border-[var(--border)] rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-[var(--accent)] resize-none" placeholder="Describe your issue in detail..."></textarea>
              </div>
              <button className="bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-xl text-sm font-medium transition-colors w-full md:w-auto">
                Submit Ticket
              </button>
            </form>
          </div>

        </div>
      </div>
    </div>
  )
}

function ResourceCard({ icon: Icon, title, desc }: any) {
  return (
    <div className="group flex items-start gap-4 p-4 rounded-xl hover:bg-[var(--surface-1)] border border-transparent hover:border-[var(--border)] transition-all cursor-pointer">
      <div className="mt-1 p-2 bg-[var(--surface-2)] rounded-lg group-hover:bg-[var(--accent-bg)] transition-colors">
        <Icon className="w-5 h-5 text-[var(--text-2)] group-hover:text-[var(--accent)] transition-colors" />
      </div>
      <div>
        <h4 className="font-medium text-[var(--text-1)] group-hover:text-white transition-colors">{title}</h4>
        <p className="text-xs text-[var(--text-2)] mt-1">{desc}</p>
      </div>
    </div>
  )
}

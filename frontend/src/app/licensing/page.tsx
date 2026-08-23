'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Check, X, Shield, Zap, Key, CreditCard, ChevronRight } from 'lucide-react'

export default function Licensing() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('annual')

  const plans = [
    {
      name: "Starter",
      desc: "For individual researchers and small projects.",
      price: billingCycle === 'annual' ? 0 : 0,
      period: "Forever Free",
      features: [
        "1,000 API calls / month",
        "Standard latency",
        "Watermark detection only",
        "Community support"
      ],
      missing: [
        "Speaker verification",
        "Prosody analysis",
        "SLA guarantee"
      ],
      cta: "Current Plan",
      primary: false
    },
    {
      name: "Pro",
      desc: "For growing teams and commercial applications.",
      price: billingCycle === 'annual' ? 49 : 59,
      period: "per user / month",
      features: [
        "50,000 API calls / month",
        "Low latency (<200ms)",
        "Full 6-layer deepfake analysis",
        "Speaker verification module",
        "Priority email support"
      ],
      missing: [
        "On-premise deployment"
      ],
      cta: "Upgrade to Pro",
      primary: true
    },
    {
      name: "Enterprise",
      desc: "For military, government, and high-volume platforms.",
      price: "Custom",
      period: "Contact us",
      features: [
        "Unlimited API calls",
        "Ultra-low latency (<50ms)",
        "Custom acoustic models",
        "On-premise deployment option",
        "24/7 dedicated support phone line",
        "Custom SLA guarantee"
      ],
      missing: [],
      cta: "Contact Sales",
      primary: false
    }
  ]

  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text-1)] font-sans pb-24">
      {/* Header */}
      <section className="pt-24 pb-16 px-6 text-center max-w-3xl mx-auto">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">Simple, transparent pricing</h1>
        <p className="text-[var(--text-2)] text-lg mb-10">
          Scale your deepfake defense infrastructure without hidden fees. All plans include our core cryptographic watermark verification.
        </p>
        
        {/* Toggle */}
        <div className="inline-flex items-center p-1 bg-[var(--surface-2)] border border-[var(--border)] rounded-full">
          <button 
            onClick={() => setBillingCycle('monthly')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${billingCycle === 'monthly' ? 'bg-[var(--surface-3)] text-white shadow-sm border border-[var(--border-strong)]' : 'text-[var(--text-2)] hover:text-[var(--text-1)]'}`}
          >
            Monthly
          </button>
          <button 
            onClick={() => setBillingCycle('annual')}
            className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${billingCycle === 'annual' ? 'bg-[var(--surface-3)] text-white shadow-sm border border-[var(--border-strong)]' : 'text-[var(--text-2)] hover:text-[var(--text-1)]'}`}
          >
            Annual <span className="text-[var(--accent)] ml-1 text-xs">Save 20%</span>
          </button>
        </div>
      </section>

      {/* Pricing Grid */}
      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan, i) => (
          <motion.div 
            key={plan.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.4 }}
            className={`relative rounded-3xl p-8 flex flex-col ${
              plan.primary 
                ? 'bg-gradient-to-b from-[var(--surface-2)] to-[var(--surface-1)] border-2 border-[var(--accent-border)] shadow-[0_0_30px_rgba(232,54,93,0.1)]' 
                : 'bg-[var(--surface-1)] border border-[var(--border)]'
            }`}
          >
            {plan.primary && (
              <div className="absolute -top-4 inset-x-0 flex justify-center">
                <span className="bg-[var(--accent)] text-white text-xs font-bold px-3 py-1 rounded-full tracking-wider uppercase">Most Popular</span>
              </div>
            )}
            
            <div className="mb-6">
              <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
              <p className="text-sm text-[var(--text-2)] h-10">{plan.desc}</p>
            </div>
            
            <div className="mb-8">
              <div className="flex items-end gap-1">
                {typeof plan.price === 'number' && <span className="text-2xl text-[var(--text-2)] font-medium">$</span>}
                <span className="text-5xl font-bold tracking-tight">{plan.price}</span>
              </div>
              <p className="text-[var(--text-2)] text-sm mt-1">{plan.period}</p>
            </div>
            
            <button className={`w-full py-3 rounded-xl font-medium transition-all mb-8 ${
              plan.primary 
                ? 'bg-[var(--text-1)] text-black hover:bg-gray-200' 
                : 'bg-transparent border border-[var(--border-strong)] text-[var(--text-1)] hover:bg-[var(--surface-2)]'
            }`}>
              {plan.cta}
            </button>
            
            <div className="space-y-4 flex-1">
              <p className="text-xs font-bold text-[var(--text-1)] tracking-wider uppercase mb-4">Includes</p>
              {plan.features.map(f => (
                <div key={f} className="flex items-start gap-3">
                  <Check className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                  <span className="text-sm text-[var(--text-1)]">{f}</span>
                </div>
              ))}
              
              {plan.missing.map(m => (
                <div key={m} className="flex items-start gap-3 opacity-40">
                  <X className="w-4 h-4 text-[var(--text-3)] mt-0.5 shrink-0" />
                  <span className="text-sm text-[var(--text-3)]">{m}</span>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Current License Status (Mocked for User) */}
      <section className="max-w-4xl mx-auto mt-24 px-6">
        <div className="bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl p-8 flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-8 opacity-5">
            <Key className="w-32 h-32" />
          </div>
          
          <div className="relative z-10 flex-1">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-[var(--accent)]" />
              <h3 className="text-lg font-semibold">Your Current License</h3>
            </div>
            <p className="text-[var(--text-2)] text-sm">You are currently on the <span className="text-[var(--text-1)] font-medium">Free Tier</span>. You have used 450 / 1,000 API calls this month.</p>
          </div>
          
          <div className="relative z-10 w-full md:w-auto">
            <div className="h-2 w-full md:w-48 bg-[var(--surface-3)] rounded-full overflow-hidden mb-2">
              <div className="h-full bg-[var(--accent)] w-[45%]" />
            </div>
            <p className="text-xs text-right text-[var(--text-3)] font-mono">45% Usage</p>
          </div>
        </div>
      </section>

    </div>
  )
}

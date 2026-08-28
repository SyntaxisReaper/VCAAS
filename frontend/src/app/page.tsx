'use client'

import React, { useRef } from 'react'
import Link from 'next/link'
import Image from 'next/image'
import { motion, useScroll, useTransform } from 'framer-motion'
import { useInView } from 'react-intersection-observer'
import {
  ArrowRight,
  Mic,
  Shield,
  Zap,
  Code2,
  Play,
  Check,
  ChevronRight,
  AudioLines,
} from 'lucide-react'

/* ─────────────────────────────────────────────────
   Constants — defined outside component to prevent
   hydration mismatches from Math.random()
   ───────────────────────────────────────────────── */

/** Deterministic waveform bar heights using sine/cosine */
const WAVE_BARS = Array.from({ length: 52 }, (_, i) => {
  const t = i / 52
  const h =
    18 +
    Math.abs(Math.sin(t * Math.PI * 7)) * 42 +
    Math.abs(Math.cos(t * Math.PI * 4.3)) * 18
  return {
    height: Math.min(80, Math.max(8, h)),
    delay: t * 2.2,
    duration: 1.4 + Math.abs(Math.sin(i * 1.7)) * 0.8,
  }
})

const FEATURES = [
  {
    icon: Mic,
    title: 'Voice Cloning',
    description:
      'Upload 30 seconds of audio and generate a high-fidelity voice model. Supports XTTS v2 for near-human quality synthesis.',
    tag: 'Core',
  },
  {
    icon: Shield,
    title: 'Ethical Licensing',
    description:
      'Every clone is tied to a legal license. Track usage, set fine-grained permissions, revoke access, and earn royalties.',
    tag: 'Legal',
  },
  {
    icon: AudioLines,
    title: '6-Layer Watermarking',
    description:
      'HMAC-signed echo-hiding embeds invisible watermarks that survive compression. Deepfake detection at the acoustic level.',
    tag: 'Security',
  },
  {
    icon: Code2,
    title: 'Developer API',
    description:
      'REST API with async job queue. Sub-2s generation, WebSocket streaming, and SDK support for Python and JavaScript.',
    tag: 'API',
  },
]

const STEPS = [
  {
    n: '01',
    title: 'Upload voice samples',
    desc: 'Provide 15–120 seconds of clean, single-speaker audio. MP3, WAV, FLAC — we handle preprocessing.',
  },
  {
    n: '02',
    title: 'Train your model',
    desc: 'Our XTTS v2 pipeline fine-tunes a personalized voice model. Training completes in minutes, not hours.',
  },
  {
    n: '03',
    title: 'Clone & deploy',
    desc: 'Hit the API to synthesize any text in your voice. Every output carries a signed acoustic watermark.',
  },
]

const STATS = [
  { value: '25+',    label: 'Trained voices'      },
  { value: '6',      label: 'Detection layers'    },
  { value: '<2s',    label: 'Generation time'     },
  { value: '99.7%',  label: 'Watermark accuracy'  },
]

const TRUSTED_FEATURES = [
  'No subscription lock-in',
  'GDPR-compliant voice storage',
  'Open licensing model',
  'REST + WebSocket API',
  'Python & JS SDKs',
  'Async job queue',
]

/* ─────────────────────────────────────────────────
   Animation Variants
   ───────────────────────────────────────────────── */

const fadeUp = {
  hidden:  { opacity: 0, y: 22 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.08,
      duration: 0.55,
      ease: [0.22, 1, 0.36, 1],
    },
  }),
}

const fadeIn = {
  hidden:  { opacity: 0 },
  visible: (i = 0) => ({
    opacity: 1,
    transition: { delay: i * 0.06, duration: 0.4 },
  }),
}

/* ─────────────────────────────────────────────────
   Reusable animated section wrapper
   ───────────────────────────────────────────────── */
function AnimSection({
  children,
  className = '',
}: {
  children: React.ReactNode
  className?: string
}) {
  const [ref, inView] = useInView({ threshold: 0.1, triggerOnce: true })
  return (
    <motion.section
      ref={ref}
      initial="hidden"
      animate={inView ? 'visible' : 'hidden'}
      className={className}
    >
      {children}
    </motion.section>
  )
}

/* ─────────────────────────────────────────────────
   Waveform Visualizer
   ───────────────────────────────────────────────── */
function WaveformVisualizer() {
  return (
    <div
      className="flex items-center justify-center gap-[3px]"
      style={{ height: 96, userSelect: 'none' }}
      aria-hidden="true"
    >
      {WAVE_BARS.map((bar, i) => (
        <motion.div
          key={i}
          style={{
            width: 2,
            borderRadius: 99,
            background: 'var(--accent)',
            originY: 1,
          }}
          animate={{
            height: [bar.height * 0.18, bar.height, bar.height * 0.18],
            opacity: [0.25, 0.75, 0.25],
          }}
          transition={{
            duration: bar.duration,
            repeat: Infinity,
            delay: bar.delay,
            ease: 'easeInOut',
          }}
        />
      ))}
    </div>
  )
}

/* ─────────────────────────────────────────────────
   Feature Card
   ───────────────────────────────────────────────── */
function FeatureCard({
  feature,
  index,
}: {
  feature: (typeof FEATURES)[0]
  index: number
}) {
  const Icon = feature.icon
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      className="surface-card p-6 flex flex-col gap-4 group cursor-default"
      whileHover={{ y: -3, transition: { duration: 0.2 } }}
    >
      <div className="flex items-start justify-between">
        <div
          style={{
            width: 40, height: 40,
            borderRadius: 'var(--radius-md)',
            background: 'var(--accent-bg)',
            border: '1px solid var(--accent-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Icon size={18} style={{ color: 'var(--accent)' }} />
        </div>
        <span className="badge badge-neutral" style={{ fontSize: 11 }}>
          {feature.tag}
        </span>
      </div>

      <div>
        <h3
          style={{
            fontSize: 15,
            fontWeight: 600,
            color: 'var(--text-1)',
            letterSpacing: '-0.015em',
            marginBottom: 6,
          }}
        >
          {feature.title}
        </h3>
        <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6 }}>
          {feature.description}
        </p>
      </div>
    </motion.div>
  )
}

/* ─────────────────────────────────────────────────
   Step Card
   ───────────────────────────────────────────────── */
function StepCard({
  step,
  index,
  isLast,
}: {
  step: (typeof STEPS)[0]
  index: number
  isLast: boolean
}) {
  return (
    <motion.div
      variants={fadeUp}
      custom={index}
      className="flex gap-5 relative"
    >
      {/* Line connector */}
      {!isLast && (
        <div
          aria-hidden="true"
          style={{
            position: 'absolute',
            left: 19,
            top: 48,
            bottom: -32,
            width: 1,
            background: 'var(--border)',
          }}
        />
      )}

      {/* Number bubble */}
      <div
        style={{
          width: 40, height: 40,
          borderRadius: 'var(--radius-md)',
          background: 'var(--surface-2)',
          border: '1px solid var(--border-mid)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
          fontFamily: 'JetBrains Mono, monospace',
          fontSize: 12,
          fontWeight: 600,
          color: 'var(--text-3)',
          letterSpacing: '0.05em',
        }}
      >
        {step.n}
      </div>

      <div style={{ paddingTop: 8, paddingBottom: 32 }}>
        <h3
          style={{
            fontSize: 16,
            fontWeight: 600,
            color: 'var(--text-1)',
            letterSpacing: '-0.015em',
            marginBottom: 6,
          }}
        >
          {step.title}
        </h3>
        <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.65 }}>
          {step.desc}
        </p>
      </div>
    </motion.div>
  )
}

/* ─────────────────────────────────────────────────
   Code Snippet
   ───────────────────────────────────────────────── */
function CodeSnippet() {
  const lines = [
    { t: 'comment', v: '# Synthesize text in any cloned voice' },
    { t: 'import',  v: 'import vcaas' },
    { t: 'blank',   v: '' },
    { t: 'code',    v: 'client = vcaas.Client(api_key="sk-...")' },
    { t: 'blank',   v: '' },
    { t: 'code',    v: 'audio = client.tts.synthesize(' },
    { t: 'param',   v: '  voice_id = "voice_rkmishra",' },
    { t: 'param',   v: '  text     = "Hello, world.",' },
    { t: 'param',   v: '  watermark= True,' },
    { t: 'code',    v: ')' },
    { t: 'blank',   v: '' },
    { t: 'code',    v: 'audio.save("output.wav")' },
  ]

  const colorMap: Record<string, string> = {
    comment: 'var(--text-3)',
    import:  '#7dd3fc',
    code:    'var(--text-1)',
    param:   '#86efac',
    blank:   'transparent',
  }

  return (
    <div className="code-block">
      {/* Dot decorations */}
      <div
        className="flex gap-1.5 mb-4"
        aria-hidden="true"
        style={{ opacity: 0.4 }}
      >
        {['#ff5f57','#ffbd2e','#28c840'].map(c => (
          <div key={c} style={{ width: 10, height: 10, borderRadius: '50%', background: c }} />
        ))}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
        {lines.map((line, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 + i * 0.06, duration: 0.3 }}
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 13,
              lineHeight: 1.7,
              color: colorMap[line.t] ?? 'var(--text-1)',
              minHeight: 22,
            }}
          >
            {line.v}
          </motion.div>
        ))}
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────
   Main Page Component
   ───────────────────────────────────────────────── */
export default function HomePage() {
  const heroRef = useRef<HTMLDivElement>(null)
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ['start start', 'end start'] })
  const heroOpacity = useTransform(scrollYProgress, [0, 0.6], [1, 0])
  const heroY       = useTransform(scrollYProgress, [0, 0.6], [0, -40])

  const [heroInView, setHeroInView] = React.useState(true)

  return (
    <div style={{ background: 'var(--bg)' }}>

      {/* ══════════════════════════════════════════
          HERO
          ══════════════════════════════════════════ */}
      <section
        ref={heroRef}
        style={{
          position: 'relative',
          minHeight: '100dvh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          paddingTop: 80,
          paddingBottom: 80,
        }}
      >
        {/* Background glow */}
        <div className="hero-glow" aria-hidden="true" />

        <motion.div
          style={{ opacity: heroOpacity, y: heroY }}
          className="container flex flex-col items-center text-center"
        >
          {/* Badge */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            custom={0}
            className="mb-8"
          >
            <span className="badge badge-accent">
              <span
                style={{
                  width: 6, height: 6,
                  borderRadius: '50%',
                  background: 'var(--accent)',
                  animation: 'pulse 2s ease-in-out infinite',
                  display: 'inline-block',
                }}
              />
              Voice Intelligence Platform
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={1}
            style={{
              fontSize: 'clamp(40px, 6vw, 72px)',
              fontWeight: 700,
              letterSpacing: '-0.04em',
              lineHeight: 1.08,
              color: 'var(--text-1)',
              maxWidth: 760,
              marginBottom: 24,
            }}
          >
            Voice cloning for<br />
            the{' '}
            <span className="text-gradient-accent">serious creator.</span>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={2}
            style={{
              fontSize: 'clamp(16px, 2vw, 19px)',
              color: 'var(--text-2)',
              maxWidth: 520,
              lineHeight: 1.65,
              marginBottom: 40,
            }}
          >
            Professional voice synthesis with ethical licensing,
            invisible watermarking, and a developer-first API.
          </motion.p>

          {/* CTAs */}
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={3}
            className="flex flex-col sm:flex-row gap-3 mb-16"
          >
            <Link
              href="/signup"
              id="hero-cta-primary"
              className="btn btn-primary"
              style={{ padding: '12px 24px', fontSize: 15 }}
            >
              Start Building
              <ArrowRight size={16} />
            </Link>
            <Link
              href="/playground"
              id="hero-cta-demo"
              className="btn btn-secondary"
              style={{ padding: '12px 24px', fontSize: 15 }}
            >
              <Play size={15} style={{ fill: 'currentColor' }} />
              Try Playground
            </Link>
          </motion.div>

          {/* Waveform */}
          <motion.div
            variants={fadeIn}
            initial="hidden"
            animate="visible"
            custom={4}
            style={{ width: '100%', maxWidth: 600 }}
          >
            <WaveformVisualizer />
            <p
              style={{
                fontSize: 12,
                color: 'var(--text-3)',
                marginTop: 10,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
              }}
            >
              Live waveform preview
            </p>
          </motion.div>
        </motion.div>

        {/* Scroll cue */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 2, duration: 0.6 }}
          style={{
            position: 'absolute',
            bottom: 32,
            left: '50%',
            transform: 'translateX(-50%)',
          }}
          aria-hidden="true"
        >
          <motion.div
            animate={{ y: [0, 6, 0] }}
            transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
            style={{
              width: 1,
              height: 40,
              background: 'linear-gradient(to bottom, var(--border-mid), transparent)',
              margin: '0 auto',
            }}
          />
        </motion.div>
      </section>

      {/* ══════════════════════════════════════════
          STATS BAR
          ══════════════════════════════════════════ */}
      <AnimSection>
        <div
          className="container"
          style={{ paddingTop: 0, paddingBottom: 80 }}
        >
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
              gap: 1,
              background: 'var(--border)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
            }}
          >
            {STATS.map((stat, i) => (
              <motion.div
                key={stat.label}
                variants={fadeUp}
                custom={i}
                style={{
                  background: 'var(--bg)',
                  padding: '28px 24px',
                  textAlign: 'center',
                }}
              >
                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 700,
                    letterSpacing: '-0.03em',
                    color: 'var(--text-1)',
                    lineHeight: 1,
                    marginBottom: 6,
                  }}
                >
                  {stat.value}
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-3)', letterSpacing: '0.02em' }}>
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </AnimSection>

      {/* ══════════════════════════════════════════
          FEATURES
          ══════════════════════════════════════════ */}
      <AnimSection>
        <div className="container" style={{ paddingBottom: 100 }}>
          {/* Section header */}
          <motion.div
            variants={fadeUp}
            className="mb-12"
            style={{ maxWidth: 480 }}
          >
            <p
              style={{
                fontSize: 12,
                fontWeight: 500,
                color: 'var(--accent)',
                letterSpacing: '0.1em',
                textTransform: 'uppercase',
                marginBottom: 12,
              }}
            >
              Platform
            </p>
            <h2
              style={{
                fontSize: 'clamp(28px, 4vw, 40px)',
                fontWeight: 700,
                letterSpacing: '-0.03em',
                color: 'var(--text-1)',
                lineHeight: 1.15,
                marginBottom: 14,
              }}
            >
              Everything you need to build with voice.
            </h2>
            <p style={{ fontSize: 15, color: 'var(--text-2)', lineHeight: 1.65 }}>
              VCaaS gives you the complete stack — from training to deployment —
              with legal guardrails built in from day one.
            </p>
          </motion.div>

          {/* Feature grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
              gap: 12,
            }}
          >
            {FEATURES.map((f, i) => (
              <FeatureCard key={f.title} feature={f} index={i} />
            ))}
          </div>
        </div>
      </AnimSection>

      {/* ══════════════════════════════════════════
          HOW IT WORKS + CODE SNIPPET
          ══════════════════════════════════════════ */}
      <AnimSection>
        <div className="container" style={{ paddingBottom: 100 }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: 64,
              alignItems: 'start',
            }}
          >
            {/* Left — Steps */}
            <div>
              <motion.div variants={fadeUp} custom={0} className="mb-10">
                <p
                  style={{
                    fontSize: 12,
                    fontWeight: 500,
                    color: 'var(--accent)',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    marginBottom: 12,
                  }}
                >
                  How it works
                </p>
                <h2
                  style={{
                    fontSize: 'clamp(26px, 3.5vw, 36px)',
                    fontWeight: 700,
                    letterSpacing: '-0.03em',
                    color: 'var(--text-1)',
                    lineHeight: 1.2,
                  }}
                >
                  From sample to production in minutes.
                </h2>
              </motion.div>

              <div>
                {STEPS.map((step, i) => (
                  <StepCard
                    key={step.n}
                    step={step}
                    index={i + 1}
                    isLast={i === STEPS.length - 1}
                  />
                ))}
              </div>
            </div>

            {/* Right — Code Snippet */}
            <motion.div variants={fadeUp} custom={1}>
              <CodeSnippet />
              <p
                style={{
                  fontSize: 12,
                  color: 'var(--text-3)',
                  marginTop: 14,
                  textAlign: 'center',
                  letterSpacing: '0.01em',
                }}
              >
                Python SDK · REST API · WebSocket streaming
              </p>
            </motion.div>
          </div>
        </div>
      </AnimSection>

      {/* ══════════════════════════════════════════
          TRUST / CHECKLIST
          ══════════════════════════════════════════ */}
      <AnimSection>
        <div className="container" style={{ paddingBottom: 100 }}>
          <div
            style={{
              background: 'var(--surface-1)',
              border: '1px solid var(--border)',
              borderRadius: 'var(--radius-xl)',
              padding: 'clamp(32px, 5vw, 56px)',
            }}
          >
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
                gap: 40,
                alignItems: 'center',
              }}
            >
              {/* Text */}
              <motion.div variants={fadeUp} custom={0}>
                <p
                  style={{
                    fontSize: 12,
                    fontWeight: 500,
                    color: 'var(--accent)',
                    letterSpacing: '0.1em',
                    textTransform: 'uppercase',
                    marginBottom: 12,
                  }}
                >
                  Built to trust
                </p>
                <h2
                  style={{
                    fontSize: 'clamp(24px, 3vw, 34px)',
                    fontWeight: 700,
                    letterSpacing: '-0.03em',
                    color: 'var(--text-1)',
                    lineHeight: 1.2,
                    marginBottom: 14,
                  }}
                >
                  Transparent, open, creator-first.
                </h2>
                <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.7 }}>
                  We believe voice ownership belongs to the creator. Every feature
                  in VCaaS is designed to protect that.
                </p>
              </motion.div>

              {/* Checklist */}
              <motion.div
                variants={fadeUp}
                custom={1}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 10,
                }}
              >
                {TRUSTED_FEATURES.map((item, i) => (
                  <motion.div
                    key={item}
                    variants={fadeIn}
                    custom={i}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      fontSize: 13,
                      color: 'var(--text-2)',
                    }}
                  >
                    <span
                      style={{
                        width: 18, height: 18,
                        borderRadius: '50%',
                        background: 'var(--accent-bg)',
                        border: '1px solid var(--accent-border)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                      }}
                    >
                      <Check size={10} color="var(--accent)" strokeWidth={2.5} />
                    </span>
                    {item}
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </div>
      </AnimSection>

      {/* ══════════════════════════════════════════
          CTA
          ══════════════════════════════════════════ */}
      <AnimSection>
        <div className="container" style={{ paddingBottom: 120 }}>
          <motion.div
            variants={fadeUp}
            custom={0}
            style={{ textAlign: 'center', maxWidth: 540, margin: '0 auto' }}
          >
            <h2
              style={{
                fontSize: 'clamp(28px, 4vw, 44px)',
                fontWeight: 700,
                letterSpacing: '-0.035em',
                color: 'var(--text-1)',
                lineHeight: 1.1,
                marginBottom: 16,
              }}
            >
              Ready to build with voice?
            </h2>
            <p
              style={{
                fontSize: 16,
                color: 'var(--text-2)',
                lineHeight: 1.65,
                marginBottom: 36,
              }}
            >
              Start with a free account. No credit card required.
              Your first voice model is on us.
            </p>

            <div className="flex flex-col sm:flex-row justify-center gap-3">
              <Link
                href="/signup"
                id="footer-cta-primary"
                className="btn btn-primary"
                style={{ padding: '13px 28px', fontSize: 15 }}
              >
                Create Free Account
                <ArrowRight size={16} />
              </Link>
              <Link
                href="/docs"
                id="footer-cta-docs"
                className="btn btn-secondary"
                style={{ padding: '13px 28px', fontSize: 15 }}
              >
                Read the Docs
                <ChevronRight size={16} />
              </Link>
            </div>
          </motion.div>
        </div>
      </AnimSection>

    </div>
  )
}

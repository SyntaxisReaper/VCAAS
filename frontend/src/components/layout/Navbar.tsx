'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Menu, X, ChevronDown } from 'lucide-react'

const NAV_LINKS = [
  { label: 'Dashboard',  href: '/dashboard'  },
  { label: 'Playground', href: '/playground' },
  { label: 'Training',   href: '/training'   },
  { label: 'Pricing',    href: '/pricing'    },
]

export function Navbar() {
  const [scrolled,    setScrolled]    = useState(false)
  const [mobileOpen,  setMobileOpen]  = useState(false)
  const pathname = usePathname()

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 14)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  // Close mobile menu on route change
  useEffect(() => { setMobileOpen(false) }, [pathname])

  const isActive = (href: string) => pathname === href

  return (
    <>
      <header
        className={`navbar ${scrolled ? 'navbar-scrolled' : ''}`}
        style={{ borderBottom: scrolled ? undefined : '1px solid transparent' }}
      >
        <div className="container flex items-center h-full gap-8">
          {/* ── Logo ─────────────────────────────── */}
          <Link
            href="/"
            id="nav-logo"
            className="flex items-center gap-2 shrink-0"
            aria-label="VCaaS home"
          >
            <span
              className="flex items-center justify-center rounded-md"
              style={{
                width: 28, height: 28,
                background: 'var(--accent)',
                borderRadius: 6,
              }}
            >
              <Zap size={14} color="#fff" strokeWidth={2.5} />
            </span>
            <span
              style={{
                fontSize: 15,
                fontWeight: 600,
                color: 'var(--text-1)',
                letterSpacing: '-0.025em',
              }}
            >
              VCaaS
            </span>
          </Link>

          {/* ── Desktop Nav ──────────────────────── */}
          <nav className="hidden md:flex items-center gap-1 flex-1" aria-label="Main navigation">
            {NAV_LINKS.map(({ label, href }) => (
              <Link
                key={href}
                href={href}
                id={`nav-${label.toLowerCase()}`}
                style={{
                  fontSize: 14,
                  fontWeight: 400,
                  color: isActive(href) ? 'var(--text-1)' : 'var(--text-2)',
                  textDecoration: 'none',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-sm)',
                  background: isActive(href) ? 'var(--surface-2)' : 'transparent',
                  transition: 'color 150ms ease, background 150ms ease',
                }}
                onMouseEnter={e => {
                  if (!isActive(href)) (e.currentTarget as HTMLElement).style.color = 'var(--text-1)'
                }}
                onMouseLeave={e => {
                  if (!isActive(href)) (e.currentTarget as HTMLElement).style.color = 'var(--text-2)'
                }}
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* ── Right Actions ────────────────────── */}
          <div className="hidden md:flex items-center gap-2 ml-auto">
            <Link
              href="/auth/login"
              id="nav-sign-in"
              style={{
                fontSize: 14,
                fontWeight: 400,
                color: 'var(--text-2)',
                textDecoration: 'none',
                padding: '6px 12px',
                borderRadius: 'var(--radius-sm)',
                transition: 'color 150ms ease',
              }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-1)' }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }}
            >
              Sign in
            </Link>
            <Link href="/auth/signup" id="nav-get-started" className="btn btn-primary" style={{ padding: '8px 16px', fontSize: 13 }}>
              Get Started
            </Link>
          </div>

          {/* ── Mobile Hamburger ─────────────────── */}
          <button
            id="nav-mobile-toggle"
            className="md:hidden ml-auto btn-icon btn"
            onClick={() => setMobileOpen(v => !v)}
            aria-label={mobileOpen ? 'Close menu' : 'Open menu'}
            aria-expanded={mobileOpen}
          >
            <AnimatePresence mode="wait" initial={false}>
              {mobileOpen
                ? <motion.span key="x"    initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <X size={18} />
                  </motion.span>
                : <motion.span key="menu" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }} transition={{ duration: 0.15 }}>
                    <Menu size={18} />
                  </motion.span>
              }
            </AnimatePresence>
          </button>
        </div>
      </header>

      {/* ── Mobile Menu ────────────────────────────── */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            id="nav-mobile-menu"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            style={{
              position: 'fixed',
              top: 60,
              left: 0,
              right: 0,
              zIndex: 99,
              background: 'rgba(0,0,0,0.95)',
              borderBottom: '1px solid var(--border)',
              backdropFilter: 'blur(16px)',
              padding: '16px',
            }}
          >
            <nav className="flex flex-col gap-1" aria-label="Mobile navigation">
              {NAV_LINKS.map(({ label, href }) => (
                <Link
                  key={href}
                  href={href}
                  style={{
                    fontSize: 15,
                    fontWeight: 400,
                    color: isActive(href) ? 'var(--accent)' : 'var(--text-1)',
                    textDecoration: 'none',
                    padding: '12px 14px',
                    borderRadius: 'var(--radius-md)',
                    background: isActive(href) ? 'var(--accent-bg)' : 'transparent',
                    display: 'block',
                    transition: 'background 150ms ease',
                  }}
                >
                  {label}
                </Link>
              ))}

              <div style={{ height: 1, background: 'var(--border)', margin: '8px 0' }} />

              <div className="flex flex-col gap-2">
                <Link href="/auth/login" className="btn btn-secondary" style={{ justifyContent: 'center' }}>
                  Sign in
                </Link>
                <Link href="/auth/signup" className="btn btn-primary" style={{ justifyContent: 'center' }}>
                  Get Started
                </Link>
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
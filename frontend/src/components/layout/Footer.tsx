'use client'

import React from 'react'
import Link from 'next/link'
import Image from 'next/image'

export function Footer() {
  return (
    <footer
      style={{
        borderTop: '1px solid var(--border)',
        padding: '60px 0 40px',
        background: 'var(--surface-1)',
        marginTop: 'auto',
      }}
    >
      <div className="container">
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 40,
          }}
        >
          <div className="flex flex-col md:flex-row justify-between items-start gap-12">
            {/* Brand */}
            <div className="max-w-xs">
              <Link
                href="/"
                className="flex items-center gap-3 mb-4"
                style={{ textDecoration: 'none' }}
                aria-label="VCaaS home"
              >
                <Image
                  src="/logo.png"
                  alt="VCaaS"
                  width={56}
                  height={56}
                  style={{ borderRadius: 10 }}
                  priority
                />
                <span style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-1)', letterSpacing: '-0.02em' }}>
                  VCaaS
                </span>
              </Link>
              <p style={{ fontSize: 14, color: 'var(--text-2)', lineHeight: 1.6 }}>
                Professional voice cloning platform with ethical licensing, 6-layer deepfake detection, acoustic watermarking, and developer-first APIs.
              </p>
            </div>

            {/* Links */}
            <div className="flex flex-wrap gap-12 md:gap-24">
              <div className="flex flex-col gap-4">
                <h4 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', margin: 0 }}>Product</h4>
                <nav className="flex flex-col gap-3" aria-label="Product navigation">
                  {[
                    { label: 'Playground', href: '/playground' },
                    { label: 'Training',   href: '/training' },
                    { label: 'Pricing',    href: '/pricing'    },
                  ].map(({ label, href }) => (
                    <Link key={href} href={href} style={{ fontSize: 14, color: 'var(--text-3)', textDecoration: 'none', transition: 'color 150ms ease' }} onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }} onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-3)' }}>
                      {label}
                    </Link>
                  ))}
                </nav>
              </div>

              <div className="flex flex-col gap-4">
                <h4 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', margin: 0 }}>Resources</h4>
                <nav className="flex flex-col gap-3" aria-label="Resources navigation">
                  {[
                    { label: 'Documentation', href: '/docs' },
                    { label: 'Help Center',   href: '/help' },
                    { label: 'API Reference', href: '/api-docs' },
                  ].map(({ label, href }) => (
                    <Link key={href} href={href} style={{ fontSize: 14, color: 'var(--text-3)', textDecoration: 'none', transition: 'color 150ms ease' }} onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }} onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-3)' }}>
                      {label}
                    </Link>
                  ))}
                </nav>
              </div>

              <div className="flex flex-col gap-4">
                <h4 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text-1)', margin: 0 }}>Legal</h4>
                <nav className="flex flex-col gap-3" aria-label="Legal navigation">
                  {[
                    { label: 'Privacy Policy', href: '/privacy' },
                    { label: 'Terms of Service', href: '/terms' },
                    { label: 'Licensing', href: '/licensing' },
                  ].map(({ label, href }) => (
                    <Link key={href} href={href} style={{ fontSize: 14, color: 'var(--text-3)', textDecoration: 'none', transition: 'color 150ms ease' }} onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }} onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-3)' }}>
                      {label}
                    </Link>
                  ))}
                </nav>
              </div>
            </div>
          </div>

          <div style={{ height: 1, background: 'var(--border)', width: '100%' }} />

          {/* Copyright */}
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p style={{ fontSize: 13, color: 'var(--text-3)', margin: 0 }}>
              © {new Date().getFullYear()} VCaaS. All rights reserved. Built for ethical creators.
            </p>
            <div className="flex gap-4">
              <a href="https://twitter.com" target="_blank" rel="noreferrer" style={{ color: 'var(--text-3)', transition: 'color 150ms ease' }} onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }} onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-3)' }}>Twitter</a>
              <a href="https://github.com" target="_blank" rel="noreferrer" style={{ color: 'var(--text-3)', transition: 'color 150ms ease' }} onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-2)' }} onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = 'var(--text-3)' }}>GitHub</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}

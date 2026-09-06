import React from 'react'
import Link from 'next/link'
import type { Metadata } from 'next'
import { Laptop } from 'lucide-react'
import { Button } from '@/components/ui/button'

export const metadata: Metadata = {
  title: 'LapIQ — Laptop Purchase Intelligence',
  description:
    'Stop comparing specs. Start making better decisions. Trusted laptop recommendations for Students, Professionals, Gamers, and Creators in India.',
}

/**
 * Homepage — Server Component.
 * Compact hero per ui-context.md (no full-screen video, no floating blobs, under 70vh).
 * Exact headline and CTA copy per ui-context.md specification.
 */
export default function HomePage() {
  return (
    <main>
      {/* ========== Navigation ========== */}
      <nav
        style={{
          borderBottom: '1px solid rgba(226, 232, 240, 0.7)',
          background: 'rgba(255, 255, 255, 0.80)',
          backdropFilter: 'blur(16px) saturate(180%)',
          WebkitBackdropFilter: 'blur(16px) saturate(180%)',
          position: 'sticky',
          top: 0,
          zIndex: 100,
        }}
        aria-label="Primary navigation"
      >
        <div
          className="container"
          style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '60px' }}
        >
          <Link href="/" aria-label="LapIQ home" style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
            <Laptop size={20} color="var(--color-primary)" aria-hidden="true" />
            <span style={{ fontFamily: 'var(--font-geist)', fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
              LapIQ
            </span>
          </Link>
          <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
            <Link href="/recommend" style={{ fontSize: '0.9375rem', color: 'var(--color-text-secondary)' }}>
              Recommend
            </Link>
            <Link href="/compare" style={{ fontSize: '0.9375rem', color: 'var(--color-text-secondary)' }}>
              Compare
            </Link>
          </div>
        </div>
      </nav>

      {/* ========== Hero ========== */}
      <section
        className="section"
        style={{ textAlign: 'center', paddingBlock: 'var(--space-3xl)' }}
        aria-labelledby="hero-heading"
      >
        <div className="container" style={{ maxWidth: '760px' }}>
          <p style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--color-accent)', marginBottom: 'var(--space-md)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Laptop Purchase Intelligence — India
          </p>
          <h1 id="hero-heading" style={{ marginBottom: 'var(--space-lg)', maxWidth: 'unset' }}>
            Stop Comparing Specs.<br />Start Making Better Decisions.
          </h1>
          <p style={{ fontSize: '1.125rem', color: 'var(--color-text-secondary)', marginBottom: 'var(--space-xl)', maxWidth: '56ch', margin: '0 auto var(--space-xl)' }}>
            Trusted recommendations built from benchmarks, prices, and real reviews.
          </p>
          <div style={{ display: 'flex', gap: 'var(--space-md)', justifyContent: 'center', flexWrap: 'wrap' }}>
            <Link href="/recommend">
              <Button id="hero-cta-btn" variant="primary" size="lg">
                Find My Laptop
              </Button>
            </Link>
            <Link href="/compare">
              <Button id="hero-compare-btn" variant="secondary" size="lg">
                Compare Models
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ========== Segment Cards ========== */}
      <section className="section" style={{ background: 'var(--color-surface-secondary)', paddingBlock: 'var(--space-2xl)' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', marginBottom: 'var(--space-xl)', fontSize: '1.5rem' }}>
            Built for every type of user
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 'var(--space-lg)' }}>
            {SEGMENTS.map(({ label, description }) => (
              <div
                key={label}
                className="card"
                style={{ textAlign: 'center' }}
              >
                <h3 style={{ fontSize: '1.125rem', marginBottom: 'var(--space-sm)' }}>{label}</h3>
                <p style={{ fontSize: '0.9375rem', maxWidth: 'unset' }}>{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ========== Trust Bar ========== */}
      <section className="section" aria-label="Platform trust signals">
        <div
          className="container"
          style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-2xl)', flexWrap: 'wrap' }}
        >
          {TRUST_ITEMS.map(({ stat, label }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <p style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-text-primary)', maxWidth: 'unset' }}>{stat}</p>
              <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', maxWidth: 'unset' }}>{label}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  )
}

const SEGMENTS = [
  { label: 'Students', description: 'Battery life and portability first. Budget-conscious picks under ₹60,000.' },
  { label: 'Professionals', description: 'Reliability and display quality for enterprise and remote work.' },
  { label: 'Gamers', description: 'Dedicated GPU, high refresh rate, and thermal performance.' },
  { label: 'Creators', description: 'Color accuracy, rendering speed, and storage for creative workflows.' },
]

const TRUST_ITEMS = [
  { stat: '10,000+', label: 'Benchmark data points' },
  { stat: '4 segments', label: 'User-specific scoring' },
  { stat: 'Zero LLM ranking', label: 'Fully deterministic engine' },
  { stat: 'Live prices', label: 'Updated continuously' },
]

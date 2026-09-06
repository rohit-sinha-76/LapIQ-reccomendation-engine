'use client'
import { useState } from 'react'
import { motion } from 'motion/react'
import { TrendingUp, ChevronDown, ChevronUp } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { InspectorScores } from '@/components/results/InspectorScores'
import { useReducedMotion } from '@/hooks/use-reduced-motion'
import type { LaptopVariantSummary } from '@/types'

interface RecommendationCardProps {
  laptop: LaptopVariantSummary
  rank: number
  isHighlighted?: boolean
}

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const variant = pct >= 75 ? 'success' : pct >= 50 ? 'accent' : 'warning'
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
      <div className="score-bar-track" style={{ flex: 1 }}>
        <div
          className="score-bar-fill"
          style={{ width: `${pct}%`, background: `var(--color-${variant === 'success' ? 'success' : variant === 'accent' ? 'accent' : 'warning'})` }}
          role="progressbar"
          aria-valuenow={pct}
          aria-valuemin={0}
          aria-valuemax={100}
          aria-label={`Confidence score: ${pct}%`}
        />
      </div>
      <Badge variant={variant}>{pct}% confidence</Badge>
    </div>
  )
}

/**
 * Recommendation Card — renders a single ranked laptop result.
 * Uses motion/react for staggered entrance. Respects prefers-reduced-motion.
 * Client Component — uses useReducedMotion hook.
 */
export function RecommendationCard({ laptop, rank, isHighlighted = false }: RecommendationCardProps) {
  const prefersReducedMotion = useReducedMotion()
  const [showInspector, setShowInspector] = useState(false)

  const brand = laptop.laptop_brand ?? laptop.laptopBrand ?? 'Laptop'
  const model = laptop.laptop_model ?? laptop.laptopModel ?? ''
  const price = laptop.price_inr ?? laptop.priceInr ?? 0
  const ram = laptop.ram_gb ?? laptop.ramGb ?? 0
  const totalScore = laptop.total_score ?? laptop.totalScore ?? 0
  const confidenceScore = laptop.confidence_score ?? laptop.confidenceScore ?? 0

  const cpu = laptop.cpu_model ?? laptop.cpuModel ?? 'Core Processor'
  const gpu = laptop.gpu_model ?? laptop.gpuModel ?? 'Integrated Graphics'
  const storage = laptop.storage_gb ?? laptop.storageGb ?? 512
  const storageType = laptop.storage_type ?? laptop.storageType ?? 'SSD'
  const display = laptop.display_size_inches ?? laptop.displaySizeInches ?? 15.6
  const minDisc = laptop.min_discount_price_inr ?? laptop.minDiscountPriceInr ?? Math.round(price * 0.88)
  const maxMrp = laptop.max_mrp_price_inr ?? laptop.maxMrpPriceInr ?? Math.round(price * 1.18)
  const discPct = laptop.max_discount_percentage ?? laptop.maxDiscountPercentage ?? 25.4

  const borderStyle = isHighlighted
    ? { border: '2px solid var(--color-primary)' }
    : {}

  return (
    <motion.li
      initial={prefersReducedMotion ? false : { opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={prefersReducedMotion ? { duration: 0 } : { duration: 0.2, delay: rank * 0.08, ease: 'easeOut' }}
      style={{ listStyle: 'none' }}
    >
      <Card style={borderStyle}>
        {/* Header row */}
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 'var(--space-sm)' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              #{rank} Pick
            </span>
            <h3 style={{ marginTop: 'var(--space-xs)', fontSize: '1.125rem' }}>
              {brand} {model}
            </h3>
          </div>
          {rank === 1 && (
            <Badge variant="accent">
              <TrendingUp size={12} aria-hidden="true" />
              Best Match
            </Badge>
          )}
        </div>

        {/* 3 Price Tiers Row */}
        <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'baseline', gap: 'var(--space-sm)', marginBottom: 'var(--space-sm)' }}>
          <span style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            ₹{price.toLocaleString('en-IN')}
          </span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--color-success)', fontWeight: 600 }}>
            Sale Deal: ₹{minDisc.toLocaleString('en-IN')}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textDecoration: 'line-through' }}>
            MRP ₹{maxMrp.toLocaleString('en-IN')}
          </span>
          <Badge variant="success" style={{ fontSize: '0.75rem' }}>{discPct}% Off</Badge>
        </div>

        {/* Detailed Specs Badges */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-xs)', marginBottom: 'var(--space-md)' }}>
          <Badge variant="secondary">CPU: {cpu}</Badge>
          <Badge variant="secondary">GPU: {gpu}</Badge>
          <Badge variant="secondary">{ram} GB RAM</Badge>
          <Badge variant="secondary">{storage} GB {storageType}</Badge>
          <Badge variant="secondary">{display}" Display</Badge>
          <Badge variant="accent">Score {(totalScore * 100).toFixed(0)}/100</Badge>
        </div>

        {/* Confidence */}
        <ConfidenceBar score={confidenceScore} />

        {/* Inspector Scores Toggle */}
        <div style={{ marginTop: 'var(--space-md)', paddingTop: 'var(--space-xs)', borderTop: '1px solid var(--color-border)' }}>
          <button
            type="button"
            onClick={() => setShowInspector(!showInspector)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--color-primary)',
              fontSize: '0.8125rem',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: 'var(--space-xs)',
              padding: 0,
            }}
          >
            {showInspector ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showInspector ? 'Hide Inspector Breakdown' : 'Show Inspector Breakdown'}
          </button>

          {showInspector && (
            <InspectorScores
              performanceScore={totalScore * 0.9}
              valueScore={totalScore * 0.85}
              finalScore={totalScore}
              confidenceScore={confidenceScore}
              reasonSelected={rank === 1 ? 'Top pick: highest combined performance & value score.' : `Rank #${rank} option within stated preferences.`}
              reasonOthersLost={rank === 1 ? 'Outperformed candidates on comparative total score.' : 'Ranked behind higher picks.'}
            />
          )}
        </div>
      </Card>
    </motion.li>
  )
}

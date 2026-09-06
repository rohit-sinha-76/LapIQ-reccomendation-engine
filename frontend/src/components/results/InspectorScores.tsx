'use client'
import React from 'react'
import { Badge } from '@/components/ui/badge'

export interface ScoringBreakdownProps {
  performanceScore: number
  valueScore: number
  batteryScore?: number
  portabilityScore?: number
  budgetFit?: number
  finalScore: number
  confidenceScore: number
  reasonSelected?: string
  reasonOthersLost?: string
}

/**
 * InspectorScores Component — renders dimensional score breakdowns and rationale.
 * Client Component for interactive result cards.
 */
export function InspectorScores({
  performanceScore,
  valueScore,
  batteryScore = 0.7,
  portabilityScore = 0.8,
  budgetFit = 0.95,
  finalScore,
  confidenceScore,
  reasonSelected,
  reasonOthersLost,
}: ScoringBreakdownProps) {
  const perfPct = Math.round(performanceScore * 100)
  const valPct = Math.round(valueScore * 100)
  const batPct = Math.round(batteryScore * 100)
  const portPct = Math.round(portabilityScore * 100)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)', marginTop: 'var(--space-md)', padding: 'var(--space-md)', background: 'var(--color-surface-secondary)', borderRadius: 'var(--radius-card)' }}>
      <h4 style={{ fontSize: '0.875rem', color: 'var(--color-text-primary)', marginBottom: 'var(--space-xs)' }}>
        Inspector Dimensional Breakdown
      </h4>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-xs)', fontSize: '0.8125rem', color: 'var(--color-text-secondary)' }}>
        <div>Performance: <strong>{perfPct}%</strong></div>
        <div>Value: <strong>{valPct}%</strong></div>
        <div>Battery: <strong>{batPct}%</strong></div>
        <div>Portability: <strong>{portPct}%</strong></div>
      </div>

      {reasonSelected && (
        <div style={{ marginTop: 'var(--space-xs)', fontSize: '0.8125rem', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
          <strong>Why Selected:</strong> {reasonSelected}
        </div>
      )}

      {reasonOthersLost && (
        <div style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', lineHeight: 1.5 }}>
          <strong>Why Others Lost:</strong> {reasonOthersLost}
        </div>
      )}
    </div>
  )
}

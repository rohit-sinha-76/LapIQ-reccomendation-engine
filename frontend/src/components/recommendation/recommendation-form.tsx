'use client'
import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import type { UserPreferencesPayload } from '@/types'

interface RecommendationFormProps {
  onSubmit: (payload: UserPreferencesPayload) => void
  isLoading?: boolean
}

const SEGMENTS = ['Students', 'Professionals', 'Gamers', 'Creators'] as const

/**
 * Recommendation intake form collecting user budget, use case, and segment.
 * Client Component — uses useState for controlled form state.
 */
export function RecommendationForm({ onSubmit, isLoading = false }: RecommendationFormProps) {
  const [budgetInr, setBudgetInr] = useState<number>(60000)
  const [useCase, setUseCase] = useState<string>('')
  const [targetSegment, setTargetSegment] = useState<UserPreferencesPayload['targetSegment']>('Students')
  const [requiresDedicatedGpu, setRequiresDedicatedGpu] = useState(false)
  const [prefersLightweight, setPrefersLightweight] = useState(false)

  function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    onSubmit({
      budgetInr,
      useCase,
      targetSegment,
      requiresDedicatedGpu,
      prefersLightweight,
    })
  }

  return (
    <form onSubmit={handleSubmit} id="recommendation-form" noValidate>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>

        {/* Budget */}
        <div>
          <label htmlFor="budget-input" className="label">
            Budget (INR)
          </label>
          <input
            id="budget-input"
            type="number"
            className="input"
            value={budgetInr}
            min={20000}
            max={500000}
            step={1000}
            required
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setBudgetInr(Number(e.target.value))}
            aria-describedby="budget-hint"
          />
          <span id="budget-hint" style={{ fontSize: '0.8125rem', color: 'var(--color-muted)', marginTop: 'var(--space-xs)', display: 'block' }}>
            ₹20,000 – ₹5,00,000
          </span>
        </div>

        {/* Use Case */}
        <div>
          <label htmlFor="usecase-input" className="label">
            What will you use it for?
          </label>
          <input
            id="usecase-input"
            type="text"
            className="input"
            value={useCase}
            placeholder="e.g. college study, video editing, competitive gaming"
            required
            minLength={2}
            maxLength={200}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUseCase(e.target.value)}
          />
        </div>

        {/* Segment */}
        <fieldset style={{ border: 'none', padding: 0 }}>
          <legend className="label" style={{ marginBottom: 'var(--space-sm)' }}>I am a</legend>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 'var(--space-sm)' }}>
            {SEGMENTS.map((seg) => (
              <label
                key={seg}
                htmlFor={`segment-${seg}`}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-xs)',
                  cursor: 'pointer',
                  fontSize: '0.9375rem',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-button)',
                  border: `1px solid ${targetSegment === seg ? 'var(--color-primary)' : 'var(--color-border)'}`,
                  background: targetSegment === seg ? '#EFF6FF' : 'var(--color-surface)',
                  color: targetSegment === seg ? 'var(--color-primary)' : 'var(--color-text-secondary)',
                  transition: 'all 200ms ease-out',
                  userSelect: 'none',
                }}
              >
                <input
                  type="radio"
                  id={`segment-${seg}`}
                  name="segment"
                  value={seg}
                  checked={targetSegment === seg}
                  onChange={() => setTargetSegment(seg)}
                  style={{ position: 'absolute', opacity: 0, width: 0, height: 0 }}
                />
                {seg}
              </label>
            ))}
          </div>
        </fieldset>

        {/* Preferences */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-sm)' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', cursor: 'pointer', fontSize: '0.9375rem', color: 'var(--color-text-secondary)' }}>
            <input
              id="dedicated-gpu-checkbox"
              type="checkbox"
              checked={requiresDedicatedGpu}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRequiresDedicatedGpu(e.target.checked)}
            />
            Needs dedicated GPU (gaming / creative workloads)
          </label>
          <label style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)', cursor: 'pointer', fontSize: '0.9375rem', color: 'var(--color-text-secondary)' }}>
            <input
              id="lightweight-checkbox"
              type="checkbox"
              checked={prefersLightweight}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPrefersLightweight(e.target.checked)}
            />
            Prefer lightweight (under 1.7 kg)
          </label>
        </div>

        <Button
          type="submit"
          variant="primary"
          size="lg"
          isLoading={isLoading}
          id="find-laptop-btn"
        >
          Find My Laptop
        </Button>
      </div>
    </form>
  )
}

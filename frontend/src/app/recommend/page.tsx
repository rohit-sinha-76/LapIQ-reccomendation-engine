'use client'
import React, { useState } from 'react'
import { RecommendationForm } from '@/components/recommendation/recommendation-form'
import { RecommendationCard } from '@/components/recommendation/recommendation-card'
import { StreamingExplanation } from '@/components/recommendation/streaming-explanation'
import { Button } from '@/components/ui/button'
import { ComparisonModal } from '@/components/results/ComparisonModal'
import type { LaptopVariantSummary, RecommendationResponse, UserPreferencesPayload } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

/**
 * Recommendation Page — entry point for user recommendation flow.
 * Client Component: manages form state, API submission, and result rendering.
 * Rendering order follows ui-context.md mandatory section order.
 */
export default function RecommendPage() {
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<RecommendationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isCompareOpen, setIsCompareOpen] = useState(false)

  async function handleSubmit(payload: UserPreferencesPayload) {
    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          budget_inr: payload.budgetInr,
          use_case: payload.useCase,
          target_segment: payload.targetSegment,
          min_ram_gb: payload.minRamGb ?? 8,
          requires_dedicated_gpu: payload.requiresDedicatedGpu ?? false,
          prefers_lightweight: payload.prefersLightweight ?? false,
        }),
      })

      if (!res.ok) {
        const body = (await res.json()) as { detail?: unknown }
        let errorMsg = 'Recommendation service unavailable.'
        if (typeof body.detail === 'string') {
          errorMsg = body.detail
        } else if (Array.isArray(body.detail) && body.detail.length > 0) {
          errorMsg = body.detail
            .map((err: { msg?: string }) => err.msg ?? 'Invalid input')
            .join('; ')
        } else if (body.detail && typeof body.detail === 'object') {
          errorMsg = JSON.stringify(body.detail)
        }
        setError(errorMsg)
        return
      }

      const data = (await res.json()) as RecommendationResponse
      setResult(data)
    } catch {
      setError('Unable to reach the recommendation service. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main>
      <div className="container section">
        <h1 style={{ marginBottom: 'var(--space-lg)' }}>Find My Laptop</h1>

        <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 2fr' : '1fr', gap: 'var(--space-xl)', alignItems: 'start' }}>

          {/* Form Column */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: 'var(--space-lg)' }}>Your preferences</h2>
            <RecommendationForm onSubmit={handleSubmit} isLoading={isLoading} />
          </div>

          {/* Results Column */}
          {result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '1.25rem' }}>Recommendations</h2>
                {result.recommendations.length > 1 && (
                  <Button variant="secondary" size="sm" onClick={() => setIsCompareOpen(true)}>
                    Compare Top Picks
                  </Button>
                )}
              </div>

              {(result.is_partial ?? result.isPartial) && (
                <p style={{ fontSize: '0.875rem', color: 'var(--color-warning)', maxWidth: 'unset' }}>
                  Fewer results than usual are available in your budget range.
                </p>
              )}

              {/* Section 1 + 2: Best Match + Confidence */}
              <ul style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-md)', padding: 0 }} aria-label="Laptop recommendations">
                {result.recommendations.map((laptop: LaptopVariantSummary, index: number) => {
                  const key = laptop.variant_id ?? laptop.variantId ?? `laptop-${index}`
                  return (
                    <RecommendationCard
                      key={key}
                      laptop={laptop}
                      rank={index + 1}
                      isHighlighted={index === 0}
                    />
                  )
                })}
              </ul>

              {/* Section 3: Streaming Explanation (Why This Laptop) */}
              {result.recommendations[0] && (
                <div className="card">
                  <StreamingExplanation
                    requestId={result.request_id ?? result.requestId ?? ''}
                    apiBaseUrl={API_BASE_URL}
                  />
                </div>
              )}

              {/* Comparison Modal */}
              <ComparisonModal
                isOpen={isCompareOpen}
                onClose={() => setIsCompareOpen(false)}
                laptops={result.recommendations}
              />
            </div>
          )}
        </div>

        {/* Error state */}
        {error && (
          <div role="alert" style={{ marginTop: 'var(--space-lg)', padding: 'var(--space-md)', background: '#FEE2E2', borderRadius: 'var(--radius-button)', color: 'var(--color-danger)', fontSize: '0.9375rem' }}>
            {error}
          </div>
        )}
      </div>
    </main>
  )
}

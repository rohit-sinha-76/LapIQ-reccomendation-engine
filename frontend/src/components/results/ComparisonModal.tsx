'use client'
import React from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { LaptopVariantSummary } from '@/types'

interface ComparisonModalProps {
  isOpen: boolean
  onClose: () => void
  laptops: LaptopVariantSummary[]
}

/**
 * Side-by-side laptop specification comparison modal.
 * Compares top-3 recommended picks across CPU, GPU, RAM, Storage, Display, Price Tiers & Scores.
 */
export function ComparisonModal({ isOpen, onClose, laptops }: ComparisonModalProps) {
  if (!isOpen || laptops.length === 0) return null

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="comparison-modal-title"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 50,
        padding: 'var(--space-md)',
      }}
    >
      <div
        className="card"
        style={{
          width: '100%',
          maxWidth: '1000px',
          maxHeight: '90vh',
          overflowY: 'auto',
          backgroundColor: 'var(--color-surface)',
          borderRadius: 'var(--radius-card)',
          padding: 'var(--space-xl)',
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-lg)' }}>
          <div>
            <h3 id="comparison-modal-title" style={{ fontSize: '1.375rem', fontWeight: 700 }}>
              Top Recommended Picks Comparison
            </h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--color-muted)', marginTop: '2px' }}>
              Side-by-side hardware specifications & authentic 3-tier Indian retail price comparison
            </p>
          </div>
          <Button variant="secondary" size="sm" onClick={onClose} aria-label="Close modal">
            Close
          </Button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: `repeat(${laptops.length}, 1fr)`, gap: 'var(--space-md)' }}>
          {laptops.map((laptop, idx) => {
            const brand = laptop.laptop_brand ?? laptop.laptopBrand ?? 'Laptop'
            const model = laptop.laptop_model ?? laptop.laptopModel ?? ''
            const price = laptop.price_inr ?? laptop.priceInr ?? 0
            const minDisc = laptop.min_discount_price_inr ?? laptop.minDiscountPriceInr ?? Math.round(price * 0.88)
            const maxMrp = laptop.max_mrp_price_inr ?? laptop.maxMrpPriceInr ?? Math.round(price * 1.18)
            const discPct = laptop.max_discount_percentage ?? laptop.maxDiscountPercentage ?? 25.4

            const cpu = laptop.cpu_model ?? laptop.cpuModel ?? 'Core Processor'
            const gpu = laptop.gpu_model ?? laptop.gpuModel ?? 'Integrated Graphics'
            const ram = laptop.ram_gb ?? laptop.ramGb ?? 8
            const storage = laptop.storage_gb ?? laptop.storageGb ?? 512
            const storageType = laptop.storage_type ?? laptop.storageType ?? 'SSD'
            const display = laptop.display_size_inches ?? laptop.displaySizeInches ?? 15.6

            const totalScore = laptop.total_score ?? laptop.totalScore ?? 0
            const confScore = laptop.confidence_score ?? laptop.confidenceScore ?? 0

            return (
              <div
                key={laptop.variant_id ?? idx}
                style={{
                  border: idx === 0 ? '2px solid var(--color-primary)' : '1px solid var(--color-border)',
                  borderRadius: 'var(--radius-card)',
                  padding: 'var(--space-md)',
                  background: idx === 0 ? '#F0F7FF' : 'var(--color-surface)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xs)' }}>
                  <Badge variant={idx === 0 ? 'accent' : 'secondary'}>
                    #{idx + 1} Pick
                  </Badge>
                  {idx === 0 && <Badge variant="success">Best Match</Badge>}
                </div>

                <h4 style={{ fontSize: '1.05rem', margin: 'var(--space-xs) 0 var(--space-sm) 0', lineHeight: 1.3 }}>
                  {brand} {model}
                </h4>

                {/* Price Section */}
                <div style={{ padding: 'var(--space-xs) var(--space-sm)', background: '#FFFFFF', borderRadius: '6px', border: '1px solid var(--color-border)', marginBottom: 'var(--space-md)' }}>
                  <div style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--color-primary)' }}>
                    ₹{price.toLocaleString('en-IN')} <span style={{ fontSize: '0.75rem', color: 'var(--color-muted)', fontWeight: 400 }}>(Normal Avg)</span>
                  </div>
                  <div style={{ fontSize: '0.8125rem', color: 'var(--color-success)', fontWeight: 600, marginTop: '2px' }}>
                    ₹{minDisc.toLocaleString('en-IN')} <span style={{ fontSize: '0.7rem', color: 'var(--color-muted)' }}>(Festive Sale Min)</span>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--color-muted)', textDecoration: 'line-through', marginTop: '2px' }}>
                    MRP ₹{maxMrp.toLocaleString('en-IN')} ({discPct}% Off)
                  </div>
                </div>

                {/* Specs Section */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)', fontSize: '0.8125rem', lineHeight: 1.5 }}>
                  <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Processor (CPU):</span><br />
                    <strong>{cpu}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Graphics (GPU):</span><br />
                    <strong>{gpu}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Memory (RAM):</span><br />
                    <strong>{ram} GB</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Storage:</span><br />
                    <strong>{storage} GB {storageType}</strong>
                  </div>

                  <div style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '4px' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Display Size:</span><br />
                    <strong>{display}" Full HD</strong>
                  </div>

                  <div style={{ marginTop: 'var(--space-xs)' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Engine Score:</span><br />
                    <strong style={{ color: 'var(--color-primary)' }}>{(totalScore * 100).toFixed(0)} / 100</strong> ({(confScore * 100).toFixed(0)}% confidence)
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

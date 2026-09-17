'use client'
import React, { useState } from 'react'
import Link from 'next/link'
import { Laptop, ArrowRight, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { LaptopVariantSummary } from '@/types'

const BENCHMARK_LAPTOPS: LaptopVariantSummary[] = [
  {
    variant_id: 101,
    laptop_brand: 'Acer',
    laptop_model: 'Aspire 14 Core i7 13th Gen',
    price_inr: 58990,
    min_discount_price_inr: 51911,
    max_mrp_price_inr: 69608,
    max_discount_percentage: 25.4,
    cpu_model: 'Intel Core i7-1355U',
    gpu_model: 'Intel Iris Xe Graphics',
    ram_gb: 16,
    storage_gb: 512,
    storage_type: 'SSD',
    display_size_inches: 14.0,
    total_score: 0.81,
    confidence_score: 0.94,
  },
  {
    variant_id: 102,
    laptop_brand: 'Lenovo',
    laptop_model: 'IdeaPad Slim 5 2.5K IPS',
    price_inr: 74990,
    min_discount_price_inr: 65991,
    max_mrp_price_inr: 88488,
    max_discount_percentage: 25.4,
    cpu_model: 'Intel Core Ultra 5 125H',
    gpu_model: 'Intel Arc Graphics',
    ram_gb: 16,
    storage_gb: 1024,
    storage_type: 'SSD',
    display_size_inches: 14.0,
    total_score: 0.82,
    confidence_score: 0.92,
  },
  {
    variant_id: 103,
    laptop_brand: 'Acer',
    laptop_model: 'Predator Helios Neo 16',
    price_inr: 129990,
    min_discount_price_inr: 114391,
    max_mrp_price_inr: 153388,
    max_discount_percentage: 25.4,
    cpu_model: 'Intel Core i7-14700HX',
    gpu_model: 'NVIDIA GeForce RTX 4060 (8GB)',
    ram_gb: 16,
    storage_gb: 1024,
    storage_type: 'SSD',
    display_size_inches: 16.0,
    total_score: 0.88,
    confidence_score: 0.96,
  },
]

export default function ComparePage() {
  const [selectedSegment, setSelectedSegment] = useState<string>('All')

  return (
    <main>
      {/* Navigation */}
      <nav
        style={{
          borderBottom: '1px solid rgba(226, 232, 240, 0.7)',
          background: 'rgba(255, 255, 255, 0.80)',
          backdropFilter: 'blur(16px)',
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
            <span style={{ fontWeight: 700, fontSize: '1.125rem', color: 'var(--color-text-primary)' }}>
              LapIQ
            </span>
          </Link>
          <div style={{ display: 'flex', gap: 'var(--space-md)', alignItems: 'center' }}>
            <Link href="/recommend" style={{ fontSize: '0.9375rem', color: 'var(--color-text-secondary)' }}>
              Recommend
            </Link>
            <Link href="/compare" style={{ fontSize: '0.9375rem', fontWeight: 600, color: 'var(--color-primary)' }}>
              Compare
            </Link>
          </div>
        </div>
      </nav>

      <div className="container section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-md)', marginBottom: 'var(--space-xl)' }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: 'var(--space-xs)' }}>Hardware Specification Comparison</h1>
            <p style={{ color: 'var(--color-text-secondary)' }}>
              Side-by-side spec and value breakdown of top benchmarked Indian market configurations.
            </p>
          </div>
          <Link href="/recommend">
            <Button variant="primary">
              Personalized Recommendation <ArrowRight size={16} style={{ marginLeft: '6px' }} />
            </Button>
          </Link>
        </div>

        {/* Comparison Table */}
        <div className="card" style={{ overflowX: 'auto', padding: 'var(--space-lg)' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '700px' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--color-surface-secondary)' }}>
                <th style={{ padding: 'var(--space-md)', color: 'var(--color-muted)', width: '22%' }}>Specification</th>
                {BENCHMARK_LAPTOPS.map((laptop, i) => (
                  <th key={laptop.variant_id} style={{ padding: 'var(--space-md)', width: '26%' }}>
                    <div style={{ fontSize: '0.8125rem', color: 'var(--color-primary)', fontWeight: 600 }}>
                      {i === 0 ? 'STUDENT BENCHMARK' : i === 1 ? 'PROFESSIONAL BENCHMARK' : 'GAMING BENCHMARK'}
                    </div>
                    <div style={{ fontSize: '1.0625rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                      {laptop.laptop_brand} {laptop.laptop_model}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Current Price</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)' }}>
                    <span style={{ fontSize: '1.125rem', fontWeight: 700, color: 'var(--color-text-primary)' }}>
                      ₹{(laptop.price_inr ?? 0).toLocaleString('en-IN')}
                    </span>
                    <span style={{ marginLeft: '8px', fontSize: '0.8125rem', color: 'var(--color-success)', fontWeight: 600 }}>
                      {laptop.max_discount_percentage ?? 0}% off MRP
                    </span>
                  </td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Processor (CPU)</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)', fontSize: '0.9375rem' }}>
                    {laptop.cpu_model}
                  </td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Graphics (GPU)</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)', fontSize: '0.9375rem' }}>
                    {laptop.gpu_model}
                  </td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Memory & Storage</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)', fontSize: '0.9375rem' }}>
                    {laptop.ram_gb} GB RAM | {laptop.storage_gb} GB {laptop.storage_type}
                  </td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Display Panel</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)', fontSize: '0.9375rem' }}>
                    {laptop.display_size_inches}&quot; IPS Anti-glare
                  </td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid var(--color-surface-secondary)' }}>
                <td style={{ padding: 'var(--space-md)', fontWeight: 600 }}>Engine Confidence Score</td>
                {BENCHMARK_LAPTOPS.map((laptop) => (
                  <td key={laptop.variant_id} style={{ padding: 'var(--space-md)' }}>
                    <Badge variant="success">
                      <CheckCircle2 size={12} style={{ marginRight: '4px' }} />
                      {Math.round((laptop.confidence_score ?? 1) * 100)}% Confidence
                    </Badge>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </main>
  )
}

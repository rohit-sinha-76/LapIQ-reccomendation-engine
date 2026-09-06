import React from 'react'

type BadgeVariant = 'default' | 'success' | 'warning' | 'accent' | 'secondary' | 'danger'

interface BadgeProps {
  children: React.ReactNode
  variant?: BadgeVariant
  className?: string
  style?: React.CSSProperties
}

const VARIANT_CLASS: Record<BadgeVariant, string> = {
  default: '',
  success: 'badge--success',
  warning: 'badge--warning',
  accent: 'badge--accent',
  secondary: '',
  danger: 'badge--warning',
}

/**
 * Shared Badge primitive for confidence indicators, segment labels, and status.
 */
export function Badge({ children, variant = 'default', className = '', style }: BadgeProps) {
  return (
    <span className={`badge ${VARIANT_CLASS[variant]} ${className}`.trim()} style={style}>
      {children}
    </span>
  )
}

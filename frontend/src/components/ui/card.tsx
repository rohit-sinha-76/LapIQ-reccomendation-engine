import React from 'react'

interface CardProps {
  children: React.ReactNode
  className?: string
  style?: React.CSSProperties
  as?: React.ElementType
}

/**
 * Shared Card surface. Flat — no glassmorphism, no nested card surfaces.
 * Border: 1px solid var(--color-border). Radius: 10px.
 */
export function Card({ children, className = '', style, as: Tag = 'div' }: CardProps) {
  return (
    <Tag className={`card ${className}`.trim()} style={style}>
      {children}
    </Tag>
  )
}

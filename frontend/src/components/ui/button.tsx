import React from 'react'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children?: React.ReactNode
  variant?: 'primary' | 'secondary'
  size?: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  type?: 'button' | 'submit' | 'reset'
  id?: string
  className?: string
  disabled?: boolean
}

/**
 * Shared Button primitive.
 * Min touch target 44x44px enforced via CSS class.
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  isLoading = false,
  disabled,
  className = '',
  ...props
}: ButtonProps) {
  const sizeClass = size === 'lg' ? 'btn--lg' : ''
  return (
    <button
      className={`btn btn--${variant} ${sizeClass} ${className}`.trim()}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? <span aria-hidden="true">Loading…</span> : children}
    </button>
  )
}

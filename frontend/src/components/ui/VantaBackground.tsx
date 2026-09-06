'use client'

import React from 'react'
import { InteractiveMeshBackground } from './InteractiveMeshBackground'

/**
 * Safe fallback component for VantaBackground.
 * Redirects to InteractiveMeshBackground to eliminate legacy CDN errors.
 */
export function VantaBackground() {
  return <InteractiveMeshBackground />
}

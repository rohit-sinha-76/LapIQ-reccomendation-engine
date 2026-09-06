'use client'

import React, { useEffect, useRef } from 'react'

interface Point {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
  baseAlpha: number
}

/**
 * Enhanced High-Visibility InteractiveMeshBackground Component
 * Renders vibrant, glowing connected 3D WebGL-style node mesh matching LapIQ theme.
 * High contrast, vivid node glows, mouse attraction lines, 60 FPS performance.
 */
export function InteractiveMeshBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let animationFrameId: number
    let width = (canvas.width = window.innerWidth)
    let height = (canvas.height = window.innerHeight)

    const points: Point[] = []
    const POINT_COUNT = Math.min(Math.floor((width * height) / 14000), 90)
    const MAX_DISTANCE = 180
    const MOUSE_RADIUS = 240

    let mouse = { x: -1000, y: -1000 }

    // Initialize vibrant node points
    for (let i = 0; i < POINT_COUNT; i++) {
      points.push({
        x: Math.random() * width,
        y: Math.random() * height,
        vx: (Math.random() - 0.5) * 1.1,
        vy: (Math.random() - 0.5) * 1.1,
        radius: Math.random() * 2.5 + 2.0, // Larger, crisp nodes (2.0 - 4.5px)
        baseAlpha: Math.random() * 0.4 + 0.6,
      })
    }

    const handleResize = () => {
      if (!canvas) return
      width = canvas.width = window.innerWidth
      height = canvas.height = window.innerHeight
    }

    const handleMouseMove = (e: MouseEvent) => {
      mouse.x = e.clientX
      mouse.y = e.clientY
    }

    const handleMouseLeave = () => {
      mouse.x = -1000
      mouse.y = -1000
    }

    window.addEventListener('resize', handleResize)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseleave', handleMouseLeave)

    // Main render loop
    const render = () => {
      ctx.clearRect(0, 0, width, height)

      // Background canvas fill (#F8FAFC)
      ctx.fillStyle = '#F8FAFC'
      ctx.fillRect(0, 0, width, height)

      // Update point positions & draw glowing nodes
      for (let i = 0; i < points.length; i++) {
        const p = points[i]

        p.x += p.vx
        p.y += p.vy

        // Bounce off canvas boundaries
        if (p.x < 0 || p.x > width) p.vx *= -1
        if (p.y < 0 || p.y > height) p.vy *= -1

        // Mouse interaction attraction
        const dxMouse = mouse.x - p.x
        const dyMouse = mouse.y - p.y
        const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse)
        if (distMouse < MOUSE_RADIUS) {
          const force = (MOUSE_RADIUS - distMouse) / MOUSE_RADIUS
          p.x += (dxMouse / distMouse) * force * 0.8
          p.y += (dyMouse / distMouse) * force * 0.8
        }

        // Draw node with glowing radial gradient
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.radius * 2.2)
        gradient.addColorStop(0, `rgba(37, 99, 235, ${p.baseAlpha})`) // Solid LapIQ Blue (#2563EB)
        gradient.addColorStop(0.5, `rgba(59, 130, 246, ${p.baseAlpha * 0.7})`)
        gradient.addColorStop(1, 'rgba(37, 99, 235, 0)')

        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius * 2.2, 0, Math.PI * 2)
        ctx.fillStyle = gradient
        ctx.fill()

        // Solid core node dot
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
        ctx.fillStyle = '#1D4ED8' // Primary Darker Blue (#1D4ED8)
        ctx.fill()
      }

      // Draw connecting mesh lines between close points
      for (let i = 0; i < points.length; i++) {
        for (let j = i + 1; j < points.length; j++) {
          const p1 = points[i]
          const p2 = points[j]

          const dx = p1.x - p2.x
          const dy = p1.y - p2.y
          const dist = Math.sqrt(dx * dx + dy * dy)

          if (dist < MAX_DISTANCE) {
            const opacity = (1 - dist / MAX_DISTANCE) * 0.55 // Increased line opacity (up to 0.55)
            ctx.beginPath()
            ctx.moveTo(p1.x, p1.y)
            ctx.lineTo(p2.x, p2.y)
            ctx.strokeStyle = `rgba(37, 99, 235, ${opacity})`
            ctx.lineWidth = 1.4 // Thicker, sharper lines
            ctx.stroke()
          }
        }

        // Connect points to mouse cursor with vibrant highlight line
        const dxMouse = points[i].x - mouse.x
        const dyMouse = points[i].y - mouse.y
        const distMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse)

        if (distMouse < MOUSE_RADIUS) {
          const opacity = (1 - distMouse / MOUSE_RADIUS) * 0.75
          ctx.beginPath()
          ctx.moveTo(points[i].x, points[i].y)
          ctx.lineTo(mouse.x, mouse.y)
          ctx.strokeStyle = `rgba(14, 165, 233, ${opacity})` // Electric cyan-blue line to cursor (#0EA5E9)
          ctx.lineWidth = 1.8
          ctx.stroke()
        }
      }

      animationFrameId = requestAnimationFrame(render)
    }

    render()

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseleave', handleMouseLeave)
      cancelAnimationFrame(animationFrameId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      id="interactive-mesh-bg"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        zIndex: -1,
        pointerEvents: 'none',
        opacity: 1.0,
      }}
      aria-hidden="true"
    />
  )
}

'use client'
import React, { useEffect, useRef, useState } from 'react'

interface StreamingExplanationProps {
  requestId: string
  apiBaseUrl?: string
}

/**
 * SSE client component for progressive explanation rendering.
 *
 * Opens a GET /api/v1/recommend/{requestId}/stream EventSource connection.
 * Appends streamed chunks to local state for progressive display.
 * Falls back silently if the stream closes with an error.
 *
 * Client Component — uses useEffect and EventSource browser API.
 */
export function StreamingExplanation({ requestId, apiBaseUrl = '' }: StreamingExplanationProps) {
  const [text, setText] = useState<string>('')
  const [isDone, setIsDone] = useState<boolean>(false)
  const [hasError, setHasError] = useState<boolean>(false)
  const sourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!requestId) return

    const url = `${apiBaseUrl}/api/v1/recommend/${encodeURIComponent(requestId)}/stream`
    const source = new EventSource(url)
    sourceRef.current = source

    source.onmessage = (event: MessageEvent<string>) => {
      if (event.data === '[DONE]') {
        setIsDone(true)
        source.close()
        return
      }
      setText((prev) => prev + event.data)
    }

    source.onerror = () => {
      setHasError(true)
      source.close()
    }

    source.addEventListener('done', () => {
      setIsDone(true)
      source.close()
    })

    return () => {
      source.close()
    }
  }, [requestId, apiBaseUrl])

  if (hasError && text.length === 0) {
    return null
  }

  return (
    <section aria-label="Why this laptop" aria-live="polite">
      <h4 style={{ marginBottom: 'var(--space-sm)', color: 'var(--color-text-primary)' }}>
        Why this laptop
      </h4>
      <p
        style={{
          whiteSpace: 'pre-wrap',
          color: 'var(--color-text-secondary)',
          lineHeight: 1.7,
        }}
        className={!isDone ? 'streaming-cursor' : undefined}
      >
        {text}
      </p>
    </section>
  )
}

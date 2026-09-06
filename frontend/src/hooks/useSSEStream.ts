'use client'
import { useEffect, useRef, useState } from 'react'

interface UseSSEStreamReturn {
  text: string
  isDone: boolean
  isFallback: boolean
  hasError: boolean
}

/**
 * Custom React hook for SSE streaming connection lifecycle.
 * Manages EventSource connection to /api/v1/recommend/{requestId}/stream.
 * Detects [DONE] signal to close gracefully, and [FALLBACK] signal for fallback rendering.
 */
export function useSSEStream(requestId: string, apiBaseUrl: string = ''): UseSSEStreamReturn {
  const [text, setText] = useState<string>('')
  const [isDone, setIsDone] = useState<boolean>(false)
  const [isFallback, setIsFallback] = useState<boolean>(false)
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

      if (event.data === '[FALLBACK]') {
        setIsFallback(true)
        return
      }

      setText((prev) => prev + event.data)
    }

    source.onerror = () => {
      setHasError(true)
      source.close()
    }

    return () => {
      source.close()
    }
  }, [requestId, apiBaseUrl])

  return { text, isDone, isFallback, hasError }
}

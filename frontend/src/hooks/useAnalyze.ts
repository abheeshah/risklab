import { useCallback, useState } from 'react'
import type { AnalyzeRequest, AnalyzeResponse } from '../types/analytics'

type AnalyzeState = {
  data: AnalyzeResponse | null
  loading: boolean
  error: string | null
  analyze: (req: AnalyzeRequest) => Promise<void>
  clearError: () => void
  setError: (message: string) => void
}

function extractError(payload: unknown): string {
  if (!payload || typeof payload !== 'object') return 'Request failed'
  const detail = (payload as { detail?: unknown }).detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && 'message' in detail) {
    return String((detail as { message: string }).message)
  }
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === 'object' && d && 'msg' in d ? String((d as { msg: string }).msg) : String(d)))
      .join('; ')
  }
  return 'Request failed'
}

export function useAnalyze(): AnalyzeState {
  const [data, setData] = useState<AnalyzeResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const analyze = useCallback(async (req: AnalyzeRequest) => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/v1/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(req),
      })
      const body = await res.json().catch(() => null)
      if (!res.ok) {
        throw new Error(extractError(body))
      }
      setData(body as AnalyzeResponse)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Network error'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const clearError = useCallback(() => setError(null), [])

  return { data, loading, error, analyze, clearError, setError }
}

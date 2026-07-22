import { useEffect } from 'react'
import { X } from 'lucide-react'

type Props = {
  message: string | null
  onClose: () => void
}

export function Toast({ message, onClose }: Props) {
  useEffect(() => {
    if (!message) return
    const t = window.setTimeout(onClose, 6000)
    return () => window.clearTimeout(t)
  }, [message, onClose])

  if (!message) return null

  return (
    <div className="toast" role="alert">
      <span>{message}</span>
      <button type="button" aria-label="Dismiss" onClick={onClose}>
        <X size={16} />
      </button>
    </div>
  )
}

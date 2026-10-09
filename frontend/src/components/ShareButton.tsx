import { useState } from 'react'
import { api } from '../lib/api'
import type { Product } from '../lib/types'

export function ShareButton({ query, response, products }: { query: string; response: string; products: Product[] }) {
  const [link, setLink] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const share = async () => {
    setLoading(true)
    try {
      const { token } = await api.createShare({ query, response, products })
      const url = `${window.location.origin}/share/${token}`
      setLink(url)
    } finally {
      setLoading(false)
    }
  }

  if (link) {
    return (
      <input
        readOnly
        value={link}
        onFocus={(e) => e.target.select()}
        className="w-full rounded-lg border border-[var(--color-border)] bg-black/30 px-2 py-1 text-xs text-[var(--color-text-muted)]"
      />
    )
  }

  return (
    <button
      onClick={share}
      disabled={loading}
      className="rounded-lg border border-[var(--color-border)] px-3 py-1.5 text-xs font-medium text-[var(--color-text-muted)] transition hover:bg-white/5"
    >
      {loading ? 'Creating link…' : 'Share this recommendation'}
    </button>
  )
}

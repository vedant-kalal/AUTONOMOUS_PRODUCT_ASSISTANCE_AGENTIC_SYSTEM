import { useState } from 'react'
import type { Product } from '../lib/types'
import { api } from '../lib/api'

function ProductCard({ product, threadId, onSaved }: { product: Product; threadId: string; onSaved?: () => void }) {
  const [saved, setSaved] = useState(false)
  const [feedback, setFeedback] = useState<1 | -1 | null>(null)
  const [showWhy, setShowWhy] = useState(false)

  const vote = async (rating: 1 | -1) => {
    setFeedback(rating)
    await api.feedback({
      product_title: product.title,
      rating,
      thread_id: threadId,
      brand: product.brand,
      category: product.category,
    })
  }

  const save = async () => {
    await api.addWishlist(product)
    setSaved(true)
    onSaved?.()
  }

  return (
    <div className="flex flex-col overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-panel)]">
      {product.thumbnail && <img src={product.thumbnail} alt={product.title} className="h-40 w-full object-cover" />}

      <div className="flex flex-1 flex-col gap-2 p-3">
        <p className="text-sm font-medium leading-snug text-[var(--color-text)]">{product.title}</p>

        <div className="flex items-baseline justify-between">
          {product.price != null ? (
            <span className="font-mono text-base text-[var(--color-amber)]">${product.price.toFixed(2)}</span>
          ) : (
            <span />
          )}
          <div className="flex items-center gap-2 text-xs text-[var(--color-text-muted)]">
            {product.rating != null && <span>★ {product.rating}</span>}
            {product.brand && <span>{product.brand}</span>}
          </div>
        </div>

        {product.why && (
          <button
            onClick={() => setShowWhy((v) => !v)}
            className="self-start text-left text-xs text-[var(--color-text-muted)] underline decoration-dotted underline-offset-2 hover:text-[var(--color-text)]"
          >
            {showWhy ? 'Hide reasoning' : 'Why this?'}
          </button>
        )}
        {showWhy && product.why && <p className="text-xs leading-relaxed text-[var(--color-text-muted)]">{product.why}</p>}

        <div className="mt-auto flex items-center gap-1.5 pt-2">
          {product.url && (
            <a
              href={product.url}
              target="_blank"
              rel="noreferrer"
              className="flex-1 rounded-lg bg-[var(--color-primary)] px-3 py-1.5 text-center text-xs font-semibold text-[var(--color-primary-ink)] transition hover:bg-[var(--color-primary-hover)]"
            >
              View
            </a>
          )}
          <button
            onClick={() => vote(1)}
            aria-label="Good recommendation"
            className={`rounded-lg border px-2 py-1.5 text-xs transition ${
              feedback === 1 ? 'border-[var(--color-primary)] text-[var(--color-primary-hover)]' : 'border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)]'
            }`}
          >
            ↑
          </button>
          <button
            onClick={() => vote(-1)}
            aria-label="Not a good fit"
            className={`rounded-lg border px-2 py-1.5 text-xs transition ${
              feedback === -1 ? 'border-[var(--color-danger)] text-[var(--color-danger)]' : 'border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)]'
            }`}
          >
            ↓
          </button>
          <button
            onClick={save}
            disabled={saved}
            aria-label="Save for later"
            className={`rounded-lg border px-2 py-1.5 text-xs transition ${
              saved ? 'border-[var(--color-primary)] text-[var(--color-primary-hover)]' : 'border-[var(--color-border)] text-[var(--color-text-muted)] hover:text-[var(--color-text)]'
            }`}
          >
            {saved ? '✓' : '♡'}
          </button>
        </div>
      </div>
    </div>
  )
}

export function ProductGallery({
  products,
  threadId,
  onSaved,
}: {
  products: Product[]
  threadId: string
  onSaved?: () => void
}) {
  const withImages = products.filter((p) => p.thumbnail)
  if (withImages.length === 0) return null

  return (
    <div className="mt-1 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {withImages.slice(0, 6).map((p, idx) => (
        <ProductCard key={`${p.title}-${idx}`} product={p} threadId={threadId} onSaved={onSaved} />
      ))}
    </div>
  )
}

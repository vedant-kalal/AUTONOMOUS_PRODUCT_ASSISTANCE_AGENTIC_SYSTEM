import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import type { WishlistItem } from '../lib/types'

const GOALS = ['Cheapest', 'Balanced', 'Highest Quality', 'Most Sustainable']

export function Sidebar({
  threadId,
  optimizationGoal,
  setOptimizationGoal,
  giftMode,
  setGiftMode,
  onNewChat,
  onSelectThread,
  wishlistVersion,
}: {
  threadId: string
  optimizationGoal: string
  setOptimizationGoal: (v: string) => void
  giftMode: boolean
  setGiftMode: (v: boolean) => void
  onNewChat: () => void
  onSelectThread: (id: string) => void
  wishlistVersion: number
}) {
  const [threads, setThreads] = useState<string[]>([])
  const [previews, setPreviews] = useState<Record<string, string>>({})
  const [wishlist, setWishlist] = useState<WishlistItem[]>([])

  useEffect(() => {
    api.listThreads().then(async ({ threads }) => {
      const list = threads.includes(threadId) ? threads : [threadId, ...threads]
      setThreads(list)
      const entries = await Promise.all(list.map(async (t) => [t, (await api.threadPreview(t)).preview] as const))
      setPreviews(Object.fromEntries(entries))
    })
  }, [threadId])

  useEffect(() => {
    api.getWishlist().then(({ items }) => setWishlist(items))
  }, [wishlistVersion])

  const removeWishlistItem = async (key: string) => {
    await api.removeWishlist(key)
    setWishlist((prev) => prev.filter((i) => i.key !== key))
  }

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col gap-5 overflow-y-auto border-r border-[var(--color-border)] bg-[var(--color-bg-elevated)] p-5">
      <div>
        <p className="font-display text-xl font-medium text-[var(--color-primary-hover)]">Trust Cart</p>
        <p className="text-xs text-[var(--color-text-muted)]">Your personal shopping assistant</p>
      </div>

      <div>
        <p className="mb-1.5 text-xs text-[var(--color-text-muted)]">Optimize for</p>
        <select
          value={optimizationGoal}
          onChange={(e) => setOptimizationGoal(e.target.value)}
          className="w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] px-2 py-1.5 text-sm"
        >
          {GOALS.map((g) => (
            <option key={g} value={g}>
              {g}
            </option>
          ))}
        </select>
      </div>

      <label className="flex cursor-pointer items-center justify-between rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] px-3 py-2 text-sm">
        <span>Shopping for someone else?</span>
        <input type="checkbox" checked={giftMode} onChange={(e) => setGiftMode(e.target.checked)} className="h-4 w-4 accent-[var(--color-primary)]" />
      </label>

      <button
        onClick={onNewChat}
        className="rounded-lg bg-[var(--color-primary)] px-3 py-2 text-sm font-semibold text-[var(--color-primary-ink)] transition hover:bg-[var(--color-primary-hover)]"
      >
        New chat
      </button>

      <div>
        <p className="mb-1.5 text-xs text-[var(--color-text-muted)]">Conversations</p>
        <div className="flex flex-col gap-0.5">
          {threads.length === 0 && <p className="text-xs text-[var(--color-text-muted)]">No conversations yet.</p>}
          {threads.map((t) => (
            <button
              key={t}
              onClick={() => onSelectThread(t)}
              disabled={t === threadId}
              className={`truncate rounded-lg px-2 py-1.5 text-left text-sm transition ${
                t === threadId ? 'bg-[var(--color-panel)] text-[var(--color-primary-hover)]' : 'text-[var(--color-text-muted)] hover:bg-white/5 hover:text-[var(--color-text)]'
              }`}
            >
              {previews[t] || t.slice(0, 8)}
            </button>
          ))}
        </div>
      </div>

      <details className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-3">
        <summary className="cursor-pointer text-xs text-[var(--color-text-muted)]">Wishlist ({wishlist.length})</summary>
        <div className="mt-3 flex flex-col gap-2">
          {wishlist.length === 0 && <p className="text-xs text-[var(--color-text-muted)]">No saved products yet.</p>}
          {wishlist.map((item) => (
            <div key={item.key} className="rounded-lg border border-[var(--color-border)] p-2">
              <p className="text-xs font-medium">
                {item.product.title}
                {item.product.price != null && <span className="font-mono text-[var(--color-amber)]"> · ${item.product.price.toFixed(2)}</span>}
              </p>
              <div className="mt-1.5 flex gap-1">
                {item.product.url && (
                  <a href={item.product.url} target="_blank" rel="noreferrer" className="flex-1 rounded bg-white/5 px-2 py-1 text-center text-xs">
                    View
                  </a>
                )}
                <button onClick={() => removeWishlistItem(item.key)} className="rounded bg-[var(--color-danger)]/15 px-2 py-1 text-xs text-[var(--color-danger)]">
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      </details>

      <p className="mt-auto font-mono text-xs text-[var(--color-text-muted)]">{threadId.slice(0, 8)}</p>
    </aside>
  )
}

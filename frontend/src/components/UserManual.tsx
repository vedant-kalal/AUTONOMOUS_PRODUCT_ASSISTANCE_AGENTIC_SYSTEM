import { useEffect } from 'react'

const SECTIONS: { title: string; body: string }[] = [
  {
    title: 'Ask for what you need',
    body: 'Type or speak what you\'re shopping for — "running shoes under $80", "a gift for my dad." No need to phrase it perfectly; just describe it like you would to a person.',
  },
  {
    title: 'Answer a few quick questions',
    body: 'For a new search, I\'ll ask 3-5 questions to narrow things down (budget, use case, preferences). Answer as many as you like, or press Skip all to search with what you\'ve already given me.',
  },
  {
    title: 'Optimize for',
    body: 'The dropdown in the sidebar changes how results get ranked and what I ask about: Cheapest sorts by lowest price, Most Sustainable favors eco-score, and so on.',
  },
  {
    title: 'Shopping for someone else?',
    body: 'Toggle this on before searching and I\'ll ask about the recipient (occasion, their preferences) instead of assuming they share your taste and sizes.',
  },
  {
    title: 'Why this?',
    body: 'Every product card has a one-line explanation for why it was picked — click it to see the reasoning behind that specific match.',
  },
  {
    title: 'Feedback and wishlist',
    body: 'Vote ↑ or ↓ on a product to tune future recommendations, or save it (♡) to your wishlist, viewable anytime from the sidebar.',
  },
  {
    title: 'Share a recommendation',
    body: 'Click "Share this recommendation" under any result to generate a read-only link — no login needed for whoever opens it.',
  },
  {
    title: 'Conversations',
    body: 'Each search lives in its own thread. Start New chat for something unrelated, or revisit any past thread from the sidebar list.',
  },
]

export function UserManual({ onClose }: { onClose: () => void }) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose()
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4"
      onClick={onClose}
    >
      <div
        className="max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-[var(--color-border)] bg-[var(--color-panel)] p-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-start justify-between">
          <div>
            <p className="font-display text-2xl font-medium text-[var(--color-text)]">How Trust Cart works</p>
            <p className="text-sm text-[var(--color-text-muted)]">A quick guide to getting the best recommendations.</p>
          </div>
          <button
            onClick={onClose}
            aria-label="Close"
            className="shrink-0 rounded-lg border border-[var(--color-border)] px-2.5 py-1.5 text-sm text-[var(--color-text-muted)] transition hover:bg-white/5 hover:text-[var(--color-text)]"
          >
            ✕
          </button>
        </div>

        <div className="flex flex-col gap-5">
          {SECTIONS.map((s) => (
            <div key={s.title}>
              <p className="mb-1 text-sm font-semibold text-[var(--color-primary-hover)]">{s.title}</p>
              <p className="text-sm leading-relaxed text-[var(--color-text-muted)]">{s.body}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

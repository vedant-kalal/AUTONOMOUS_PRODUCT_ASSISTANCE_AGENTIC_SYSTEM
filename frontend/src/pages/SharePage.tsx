import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { api } from '../lib/api'
import type { Product } from '../lib/types'

export function SharePage() {
  const { token } = useParams<{ token: string }>()
  const [data, setData] = useState<{ query: string; response: string; products: Product[] } | null>(null)
  const [notFound, setNotFound] = useState(false)

  useEffect(() => {
    if (!token) return
    api
      .getShare(token)
      .then(setData)
      .catch(() => setNotFound(true))
  }, [token])

  return (
    <div className="tc-canvas min-h-screen bg-[var(--color-bg)]">
      <div className="mx-auto max-w-2xl px-6 py-10">
        <p className="font-display text-2xl font-medium text-[var(--color-primary-hover)]">Trust Cart</p>
        <p className="mb-6 text-sm text-[var(--color-text-muted)]">Shared recommendation</p>

        {notFound && (
          <div className="rounded-lg border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 p-4 text-sm text-[var(--color-danger)]">
            This shared link is invalid or has expired.
          </div>
        )}

        {data && (
          <>
            <p className="mb-4 text-sm text-[var(--color-text-muted)]">Originally asked: "{data.query}"</p>
            <div className="max-w-none text-[0.95rem] leading-relaxed text-[var(--color-text)] [&_ul]:list-disc [&_ul]:pl-5 [&_img]:my-2 [&_img]:max-h-48 [&_img]:rounded-lg [&_img]:object-cover [&_a]:text-[var(--color-primary-hover)] [&_p]:my-2">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>{data.response}</ReactMarkdown>
            </div>

            {data.products.filter((p) => p.thumbnail).length > 0 && (
              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                {data.products
                  .filter((p) => p.thumbnail)
                  .slice(0, 6)
                  .map((p, i) => (
                    <div key={i} className="overflow-hidden rounded-xl border border-[var(--color-border)] bg-[var(--color-panel)]">
                      <img src={p.thumbnail!} alt={p.title} className="h-32 w-full object-cover" />
                      <div className="p-3">
                        <p className="text-sm font-medium">{p.title}</p>
                        {p.url && (
                          <a
                            href={p.url}
                            target="_blank"
                            rel="noreferrer"
                            className="mt-2 block rounded-lg bg-[var(--color-primary)] px-3 py-1.5 text-center text-sm font-medium text-[var(--color-primary-ink)]"
                          >
                            View product
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </>
        )}

        <p className="mt-8 text-xs text-[var(--color-text-muted)]">
          This is a read-only shared view. Open Trust Cart to start your own search.
        </p>
      </div>
    </div>
  )
}

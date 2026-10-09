import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { ChatMessage } from '../lib/types'
import { ProductGallery } from './ProductGallery'
import { ShareButton } from './ShareButton'

function Markdown({ text }: { text: string }) {
  return (
    <div className="max-w-none text-[0.95rem] leading-relaxed text-[var(--color-text)] [&_a]:text-[var(--color-primary-hover)] [&_h3]:mt-3 [&_h3]:mb-1 [&_h3]:font-display [&_h3]:text-lg [&_h3]:font-medium [&_h4]:mt-2 [&_h4]:mb-1 [&_h4]:text-sm [&_h4]:font-semibold [&_img]:my-2 [&_img]:max-h-48 [&_img]:rounded-lg [&_img]:object-cover [&_ul]:my-1.5 [&_ul]:list-disc [&_ul]:pl-5 [&_li]:my-0.5 [&_p]:my-2 [&_strong]:text-[var(--color-text)]">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
    </div>
  )
}

export function ChatBubble({
  message,
  threadId,
  priorQuery,
  onWishlistSaved,
}: {
  message: ChatMessage
  threadId: string
  priorQuery: string
  onWishlistSaved?: () => void
}) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-[var(--color-primary)] px-4 py-2.5 text-sm text-[var(--color-primary-ink)]">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col gap-1">
      {message.qaPairs ? (
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <p className="mb-3 text-xs font-medium tracking-wide text-[var(--color-text-muted)]">Your answers</p>
          <div className="flex flex-col gap-2.5">
            {message.qaPairs.map((qa, i) => (
              <div key={i}>
                <p className="text-xs text-[var(--color-text-muted)]">{qa.question}</p>
                <p className="text-sm font-medium text-[var(--color-primary-hover)]">{qa.answer}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="max-w-2xl">
          <Markdown text={message.content} />
        </div>
      )}

      {message.products && message.products.length > 0 && (
        <>
          <ProductGallery products={message.products} threadId={threadId} onSaved={onWishlistSaved} />
          <div className="mt-1">
            <ShareButton query={priorQuery} response={message.content} products={message.products} />
          </div>
        </>
      )}
    </div>
  )
}

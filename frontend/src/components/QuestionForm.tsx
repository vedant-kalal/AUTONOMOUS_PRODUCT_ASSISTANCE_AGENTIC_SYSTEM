import { useState } from 'react'

export function QuestionForm({
  questions,
  onSubmit,
  onSkip,
}: {
  questions: string[]
  onSubmit: (answers: Record<string, string>) => void
  onSkip: () => void
}) {
  const [answers, setAnswers] = useState<Record<string, string>>({})

  const setAnswer = (q: string, v: string) => setAnswers((prev) => ({ ...prev, [q]: v }))

  const submit = () => {
    const filled = Object.fromEntries(Object.entries(answers).filter(([, v]) => v.trim()))
    if (Object.keys(filled).length === 0) return
    onSubmit(filled)
  }

  return (
    <div className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-panel)] p-5">
      <p className="font-display text-lg font-medium text-[var(--color-text)]">A few quick questions</p>
      <p className="mb-4 text-sm text-[var(--color-text-muted)]">Answer what you can — the more I know, the better the match.</p>

      <div className="flex flex-col gap-4">
        {questions.map((q, i) => (
          <div key={q} className="flex items-start gap-3">
            <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-xs font-bold text-[var(--color-primary-ink)]">
              {i + 1}
            </span>
            <div className="flex-1">
              <p className="mb-1.5 text-sm text-[var(--color-text)]">{q}</p>
              <input
                type="text"
                placeholder="Your answer..."
                onChange={(e) => setAnswer(q, e.target.value)}
                className="w-full rounded-lg border border-[var(--color-border)] bg-black/20 px-3 py-2 text-sm outline-none focus:border-[var(--color-primary)]"
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-5 flex gap-2">
        <button
          onClick={submit}
          className="flex-1 rounded-lg bg-[var(--color-primary)] px-3 py-2 text-sm font-medium text-[var(--color-primary-ink)] transition hover:bg-[var(--color-primary-hover)]"
        >
          Submit answers
        </button>
        <button
          onClick={onSkip}
          className="flex-1 rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm font-medium text-[var(--color-text-muted)] transition hover:bg-white/5"
        >
          Skip all
        </button>
      </div>
    </div>
  )
}

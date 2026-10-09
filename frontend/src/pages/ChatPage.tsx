import { useEffect, useRef, useState } from 'react'
import { api } from '../lib/api'
import type { ChatMessage } from '../lib/types'
import { Sidebar } from '../components/Sidebar'
import { ChatBubble } from '../components/ChatBubble'
import { QuestionForm } from '../components/QuestionForm'
import { VoiceInput } from '../components/VoiceInput'
import { UserManual } from '../components/UserManual'

const THREAD_KEY = 'tc_thread_id'

const EXAMPLE_PROMPTS = ['Running shoes under $80', 'A birthday gift for my dad', 'Wireless earbuds for the gym', 'A backpack for daily commuting']

function loadHistory(threadId: string): ChatMessage[] {
  try {
    const raw = localStorage.getItem(`tc_history_${threadId}`)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

function saveHistory(threadId: string, messages: ChatMessage[]) {
  localStorage.setItem(`tc_history_${threadId}`, JSON.stringify(messages))
}

export function ChatPage() {
  const [threadId, setThreadId] = useState<string>('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [optimizationGoal, setOptimizationGoal] = useState('Balanced')
  const [giftMode, setGiftMode] = useState(false)
  const [pendingQuestions, setPendingQuestions] = useState<string[] | null>(null)
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [wishlistVersion, setWishlistVersion] = useState(0)
  const [showManual, setShowManual] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  // Synchronous guard against double-fired clicks/events — state updates aren't
  // synchronous, so a `loading` state check alone can't catch two calls in the same tick.
  const inFlightRef = useRef(false)

  useEffect(() => {
    const existing = localStorage.getItem(THREAD_KEY)
    if (existing) {
      setThreadId(existing)
      setMessages(loadHistory(existing))
    } else {
      api.createThread().then(({ thread_id }) => {
        localStorage.setItem(THREAD_KEY, thread_id)
        setThreadId(thread_id)
      })
    }
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, pendingQuestions])

  const pushMessage = (msg: ChatMessage) => {
    setMessages((prev) => {
      const next = [...prev, msg]
      saveHistory(threadId, next)
      return next
    })
  }

  const send = async (text: string) => {
    if (!text.trim() || !threadId || inFlightRef.current) return
    inFlightRef.current = true
    setError(null)
    pushMessage({ role: 'user', content: text })
    setInput('')
    setLoading(true)
    try {
      const res = await api.chat({ thread_id: threadId, message: text, optimization_goal: optimizationGoal, is_gift: giftMode })
      handleResponse(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
      inFlightRef.current = false
    }
  }

  const handleResponse = (res: { status: string; questions?: string[]; response?: string; products?: any[]; message?: string }) => {
    if (res.status === 'awaiting_answers' && res.questions) {
      setPendingQuestions(res.questions)
    } else if (res.status === 'complete') {
      setPendingQuestions(null)
      pushMessage({ role: 'assistant', content: res.response || '', products: res.products })
    } else {
      setError(res.message || 'Something went wrong.')
    }
  }

  const submitAnswers = async (answers: Record<string, string>) => {
    if (inFlightRef.current) return
    inFlightRef.current = true
    setPendingQuestions(null)
    setLoading(true)
    setError(null)
    pushMessage({
      role: 'assistant',
      content: '',
      qaPairs: Object.entries(answers).map(([question, answer]) => ({ question, answer })),
    })
    try {
      const res = await api.resume({ thread_id: threadId, answers })
      handleResponse(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
      inFlightRef.current = false
    }
  }

  const skipAnswers = async () => {
    if (inFlightRef.current) return
    inFlightRef.current = true
    setPendingQuestions(null)
    setLoading(true)
    setError(null)
    pushMessage({ role: 'assistant', content: '', qaPairs: [{ question: 'Did you answer the questions?', answer: 'No, skipped.' }] })
    try {
      const res = await api.resume({ thread_id: threadId, skipped: true })
      handleResponse(res)
    } catch (e: any) {
      setError(e.message)
    } finally {
      inFlightRef.current = false
      setLoading(false)
    }
  }

  const newChat = async () => {
    const { thread_id } = await api.createThread()
    localStorage.setItem(THREAD_KEY, thread_id)
    setThreadId(thread_id)
    setMessages([])
    setPendingQuestions(null)
  }

  const selectThread = (id: string) => {
    localStorage.setItem(THREAD_KEY, id)
    setThreadId(id)
    setMessages(loadHistory(id))
    setPendingQuestions(null)
  }

  const priorQueryFor = (index: number): string => {
    for (let i = index - 1; i >= 0; i--) {
      if (messages[i].role === 'user') return messages[i].content
    }
    return ''
  }

  if (!threadId) return null

  const isEmpty = messages.length === 0 && !pendingQuestions

  return (
    <div className="flex h-screen">
      <Sidebar
        threadId={threadId}
        optimizationGoal={optimizationGoal}
        setOptimizationGoal={setOptimizationGoal}
        giftMode={giftMode}
        setGiftMode={setGiftMode}
        onNewChat={newChat}
        onSelectThread={selectThread}
        wishlistVersion={wishlistVersion}
      />

      <main className="tc-canvas relative flex flex-1 flex-col overflow-hidden">
        <button
          onClick={() => setShowManual(true)}
          aria-label="How Trust Cart works"
          title="How Trust Cart works"
          className="absolute top-4 right-4 z-10 flex h-8 w-8 items-center justify-center rounded-full border border-[var(--color-border)] bg-[var(--color-panel)] text-sm font-medium text-[var(--color-text-muted)] transition hover:border-[var(--color-primary)] hover:text-[var(--color-text)]"
        >
          i
        </button>

        {showManual && <UserManual onClose={() => setShowManual(false)} />}

        {isEmpty ? (
          <div className="flex flex-1 flex-col items-center justify-center px-6">
            <p className="font-display text-4xl font-medium text-[var(--color-text)] sm:text-5xl">What are you shopping for?</p>
            <p className="mt-3 max-w-md text-center text-[var(--color-text-muted)]">
              Tell me what you need — I'll ask a couple of quick questions, then find real options and explain why each one fits.
            </p>
            <div className="mt-8 flex max-w-xl flex-wrap justify-center gap-2">
              {EXAMPLE_PROMPTS.map((p) => (
                <button
                  key={p}
                  onClick={() => send(p)}
                  className="rounded-full border border-[var(--color-border)] bg-[var(--color-panel)] px-4 py-2 text-sm text-[var(--color-text-muted)] transition hover:border-[var(--color-primary)] hover:text-[var(--color-text)]"
                >
                  {p}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto flex max-w-4xl flex-col gap-6 px-8 py-8">
              {messages.map((m, i) => (
                <ChatBubble key={i} message={m} threadId={threadId} priorQuery={priorQueryFor(i)} onWishlistSaved={() => setWishlistVersion((v) => v + 1)} />
              ))}

              {pendingQuestions && <QuestionForm questions={pendingQuestions} onSubmit={submitAnswers} onSkip={skipAnswers} />}

              {loading && (
                <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--color-primary)]" />
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--color-primary)] [animation-delay:150ms]" />
                  <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--color-primary)] [animation-delay:300ms]" />
                  <span className="ml-1">Thinking</span>
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-[var(--color-danger)]/40 bg-[var(--color-danger)]/10 p-3 text-sm text-[var(--color-danger)]">
                  {error}
                </div>
              )}

              <div ref={bottomRef} />
            </div>
          </div>
        )}

        {!pendingQuestions && (
          <form
            onSubmit={(e) => {
              e.preventDefault()
              send(input)
            }}
            className="mx-auto flex w-full max-w-4xl items-center gap-2 px-8 pb-6"
          >
            <VoiceInput onTranscript={(text) => send(text)} />
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about anything you'd like to buy..."
              disabled={loading}
              className="flex-1 rounded-xl border border-[var(--color-border)] bg-[var(--color-panel)] px-4 py-3 text-sm outline-none focus:border-[var(--color-primary)]"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-[var(--color-primary)] px-5 py-3 text-sm font-semibold text-[var(--color-primary-ink)] transition hover:bg-[var(--color-primary-hover)] disabled:opacity-40"
            >
              Send
            </button>
          </form>
        )}
      </main>
    </div>
  )
}

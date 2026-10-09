import { useRef, useState } from 'react'

// Uses the browser's native Web Speech API — no backend or API key needed.
// Supported in Chrome/Edge; gracefully hides itself elsewhere.
type SpeechRecognitionLike = {
  lang: string
  continuous: boolean
  interimResults: boolean
  onresult: ((e: any) => void) | null
  onerror: ((e: any) => void) | null
  onend: (() => void) | null
  start: () => void
  stop: () => void
}

function getRecognition(): SpeechRecognitionLike | null {
  const w = window as any
  const Ctor = w.SpeechRecognition || w.webkitSpeechRecognition
  return Ctor ? new Ctor() : null
}

export function VoiceInput({ onTranscript }: { onTranscript: (text: string) => void }) {
  const [recording, setRecording] = useState(false)
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null)
  const supported = typeof window !== 'undefined' && !!(window as any).webkitSpeechRecognition || !!(window as any).SpeechRecognition

  if (!supported) return null

  const toggle = () => {
    if (recording) {
      recognitionRef.current?.stop()
      setRecording(false)
      return
    }
    const recognition = getRecognition()
    if (!recognition) return
    recognition.lang = 'en-US'
    recognition.continuous = false
    recognition.interimResults = false
    recognition.onresult = (e: any) => {
      const text = e.results[0][0].transcript
      onTranscript(text)
    }
    recognition.onerror = () => setRecording(false)
    recognition.onend = () => setRecording(false)
    recognitionRef.current = recognition
    recognition.start()
    setRecording(true)
  }

  return (
    <button
      type="button"
      onClick={toggle}
      className={`rounded-lg border px-3 py-2 text-sm transition ${
        recording ? 'border-rose-500 bg-rose-500/15 text-rose-400 animate-pulse' : 'border-[var(--color-border)] hover:bg-white/5'
      }`}
      title={recording ? 'Stop recording' : 'Record voice input'}
    >
      {recording ? '⏹️ Stop' : '🎤'}
    </button>
  )
}

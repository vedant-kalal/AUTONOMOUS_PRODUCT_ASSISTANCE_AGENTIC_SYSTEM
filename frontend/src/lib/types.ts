export interface Product {
  title: string
  price?: number | null
  description?: string | null
  category?: string | null
  brand?: string | null
  url?: string | null
  thumbnail?: string | null
  rating?: number | null
  why?: string | null
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  products?: Product[]
  qaPairs?: { question: string; answer: string }[]
}

export interface ChatResponse {
  status: 'awaiting_answers' | 'complete' | 'error'
  questions?: string[]
  response?: string
  products?: Product[]
  message?: string
}

export interface WishlistItem {
  key: string
  product: Product
  saved_at: string
}

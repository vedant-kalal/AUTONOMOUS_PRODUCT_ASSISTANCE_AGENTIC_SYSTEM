import type { ChatResponse, Product, WishlistItem } from './types'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  createThread: () => request<{ thread_id: string }>('/threads', { method: 'POST' }),
  listThreads: () => request<{ threads: string[] }>('/threads'),
  threadPreview: (threadId: string) => request<{ preview: string }>(`/threads/${threadId}/preview`),
  deleteThread: (threadId: string) => request<{ ok: boolean }>(`/threads/${threadId}`, { method: 'DELETE' }),

  chat: (body: { thread_id: string; message: string; optimization_goal: string; is_gift: boolean }) =>
    request<ChatResponse>('/chat', { method: 'POST', body: JSON.stringify(body) }),

  resume: (body: { thread_id: string; answers?: Record<string, string>; skipped?: boolean }) =>
    request<ChatResponse>('/chat/resume', { method: 'POST', body: JSON.stringify(body) }),

  getWishlist: () => request<{ items: WishlistItem[] }>('/wishlist'),
  addWishlist: (product: Product) => request<{ ok: boolean }>('/wishlist', { method: 'POST', body: JSON.stringify({ product }) }),
  removeWishlist: (key: string) => request<{ ok: boolean }>(`/wishlist/${key}`, { method: 'DELETE' }),

  feedback: (body: { product_title: string; rating: number; thread_id: string; brand?: string | null; category?: string | null }) =>
    request<{ ok: boolean }>('/feedback', { method: 'POST', body: JSON.stringify(body) }),

  createShare: (body: { query: string; response: string; products: Product[] }) =>
    request<{ token: string }>('/share', { method: 'POST', body: JSON.stringify(body) }),
  getShare: (token: string) => request<{ query: string; response: string; products: Product[] }>(`/share/${token}`),
}

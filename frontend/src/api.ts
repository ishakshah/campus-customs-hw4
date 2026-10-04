import type { ChatReply, Product, ProductDetail, RegisterInput, StoredMessage, User } from './types'

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) throw new Error(res.status === 404 ? 'not-found' : `Request failed (${res.status})`)
  return res.json() as Promise<T>
}

export const getProducts = () => getJson<Product[]>('/api/products')
export const getProduct = (id: string) => getJson<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

export const formatPrice = (price: number) =>
  price.toLocaleString('en-US', { style: 'currency', currency: 'USD' })

export const NO_DESCRIPTION = 'More details coming soon.'

// Keeps hover text short enough for the photo-sized overlay. Shortens at a whole
// sentence or clause and never adds "...".
export function fitDescription(text: string, maxChars = 200): string {
  const full = text.trim()
  if (!full) return NO_DESCRIPTION
  if (full.length <= maxChars) return full
  const sentences = full.match(/[^.!?]+[.!?]+(\s|$)/g) ?? []
  let out = ''
  for (const sentence of sentences) {
    if ((out + sentence).trim().length > maxChars) break
    out += sentence
  }
  if (out.trim()) return out.trim()
  const head = full.slice(0, maxChars)
  const cut = Math.max(head.lastIndexOf(', '), head.lastIndexOf('; '))
  const clause = (cut > 0 ? head.slice(0, cut) : head.replace(/\s+\S*$/, '')).replace(/[,;:\s]+$/, '')
  return `${clause}.`
}

// ---- Accounts ----

export class ApiError extends Error {}

async function sendJson<T>(url: string, body?: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => null)
    const detail = typeof data?.detail === 'string' ? data.detail : 'Something went wrong. Please check your details and try again.'
    throw new ApiError(detail)
  }
  return res.status === 204 ? (undefined as T) : (res.json() as Promise<T>)
}

export interface AuthReply {
  user: User | null
  /** True when the password they signed in with no longer meets the current rules. */
  password_update_required: boolean
}

export const getCurrentUser = () => getJson<AuthReply>('/api/auth/me')
export const registerAccount = (input: RegisterInput) => sendJson<AuthReply>('/api/auth/register', input)
export const logIn = (email: string, password: string) => sendJson<AuthReply>('/api/auth/login', { email, password })
export const logOut = () => sendJson<void>('/api/auth/logout')
export const updatePassword = (current_password: string, new_password: string, confirm_password: string) =>
  sendJson<AuthReply>('/api/auth/change-password', { current_password, new_password, confirm_password })

// ---- Personal Assistant chat ----

export interface ChatPage {
  path: string
  showing_results: boolean
}

// `history` is used for guests; for signed-in shoppers the server loads their saved history itself.
export const sendChat = (
  message: string,
  history: { role: 'user' | 'assistant'; content: string }[],
  page: ChatPage,
) => sendJson<ChatReply>('/api/chat', { message, history, page })
export const getChatHistory = () => getJson<StoredMessage[]>('/api/chat/history')

import { useEffect, useRef, useState } from 'react'
import type { FormEvent, KeyboardEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { formatPrice, getChatHistory, sendChat } from '../api'
import { useAuth } from '../AuthContext'
import { useSearchResults } from '../ResultsContext'
import type { ProductCard } from '../types'

interface Message {
  role: 'user' | 'assistant'
  text: string
  products?: ProductCard[]
  isError?: boolean
}

const MAX_HISTORY_SENT = 12

// Playful status lines shown while the assistant works on an answer.
const THINKING_LINES = [
  'Warming up the saxophone...',
  'Consulting the inventory...',
  'Crunching the numbers (honest ones)...',
  'Shaking hands with the catalogue...',
  'Building you a bridge to a good fit...',
]

// One-tap questions, styled like campaign planks. The label is the fun part; the text is what gets sent.
const STARTERS = [
  { label: 'The Hoodie Platform', text: 'What hoodies do you have?' },
  { label: 'Gifts under $50', text: 'Show me gift ideas under $50.' },
  { label: 'Size check', text: 'What do you have in stock in medium?' },
  { label: 'Surprise me', text: 'Surprise me with a few ideas for a Yale fan.' },
]

/** A little saxophone, drawn in SVG so it takes the color of the text around it. */
function SaxIcon({ size = 22 }: { size?: number }) {
  return (
    <svg className="sax" width={size} height={size} viewBox="0 0 48 48" aria-hidden="true">
      <path d="M10 7l11 5v22a8 8 0 0 0 16 0V25" fill="none" stroke="currentColor" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M31 25h13l3-10H28z" fill="currentColor" />
      <circle cx="21" cy="19" r="1.8" fill="#fff" />
      <circle cx="21" cy="26" r="1.8" fill="#fff" />
      <circle cx="21" cy="33" r="1.8" fill="#fff" />
    </svg>
  )
}

// Older stored replies may contain markdown bold markers; the chat shows plain text.
const plain = (text: string) => text.replace(/\*\*/g, '')

export default function ChatWidget() {
  const { user } = useAuth()
  const { results, showResults } = useSearchResults()
  const navigate = useNavigate()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [draft, setDraft] = useState('')
  const [pending, setPending] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  const [thinking, setThinking] = useState(0)
  const returning = messages.length > 0
  const greeting: Message = {
    role: 'assistant',
    text: user
      ? returning
        ? `Welcome back, ${user.first_name}! The Comeback Kid returns. Pull up a chair and tell me what you're hunting for.`
        : `Well, hello there, ${user.first_name}! I never forget a name, and I won't forget yours. What can I help you find today?`
      : "Well, hello there, friend! I'm your Personal Assistant, with a little Yale Law spirit, class of '73 in the vibes. What can I help you find today?",
  }

  // Rotate the playful status line while an answer is on the way.
  useEffect(() => {
    if (!pending) return
    const timer = window.setInterval(() => setThinking((n) => (n + 1) % THINKING_LINES.length), 1800)
    return () => {
      window.clearInterval(timer)
      setThinking(0)
    }
  }, [pending])

  // Signed-in shoppers get their earlier conversation back.
  useEffect(() => {
    if (!user) return
    let cancelled = false // keeps a repeated effect run (React strict mode) from adding the history twice
    getChatHistory()
      .then((stored) => {
        if (cancelled) return
        setMessages((current) => [
          ...stored.map((m): Message => ({ role: m.role, text: plain(m.content), products: m.products })),
          ...current,
        ])
      })
      .catch(() => {})
    return () => {
      cancelled = true
    }
  }, [user])

  useEffect(() => {
    endRef.current?.scrollIntoView({ block: 'end' })
  }, [messages, pending, open])

  // Other parts of the site (like the About page) can open the assistant.
  useEffect(() => {
    const openChat = () => setOpen(true)
    window.addEventListener('open-assistant', openChat)
    return () => window.removeEventListener('open-assistant', openChat)
  }, [])

  const send = async (override?: string) => {
    const text = (override ?? draft).trim()
    if (!text || pending) return
    const history = messages
      .filter((m) => !m.isError)
      .slice(-MAX_HISTORY_SENT)
      .map((m) => ({ role: m.role, content: m.text }))
    setMessages((m) => [...m, { role: 'user', text }])
    setDraft('')
    setPending(true)
    try {
      // Tell the assistant which page the shopper is on, so "this" on a product page means that product.
      const reply = await sendChat(text, history, { path: location.pathname, showing_results: results !== null })
      setMessages((m) => [...m, { role: 'assistant', text: plain(reply.message), products: reply.products }])
      if (reply.results) {
        // The assistant searched for a type of item: show every match as cards on the Products page.
        showResults(reply.results)
        navigate('/products')
      }
    } catch (err) {
      const text = err instanceof Error ? err.message : 'Something went wrong. Please try again.'
      setMessages((m) => [...m, { role: 'assistant', text, isError: true }])
    } finally {
      setPending(false)
    }
  }

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    void send()
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void send()
    }
  }

  return (
    <div className="chat">
      {open && (
        <section className="chat__panel" aria-label="Personal Assistant">
          <header className="chat__header">
            <span className="chat__avatar chat__avatar--photo">
              <img
                src="/assistant-portrait.jpg"
                alt="Official White House portrait of Bill Clinton, used for the parody assistant character"
                width={64}
                height={64}
              />
              <span className="chat__avatar-badge" aria-hidden="true">
                <SaxIcon size={14} />
              </span>
            </span>
            <div className="chat__title">
              <strong>Personal Assistant</strong>
              <span>The Comeback Kid &middot; a Yale Law alum-inspired AI</span>
            </div>
            <button type="button" className="chat__close" onClick={() => setOpen(false)} aria-label="Close chat">
              &times;
            </button>
          </header>
          <p className="chat__disclaimer">A playful AI persona inspired by Bill Clinton, a Yale Law alum. Not the real Bill Clinton, and not endorsed by him.</p>
          <div className="chat__messages" role="log" aria-live="polite">
            {[greeting, ...messages].map((m, i) => (
              <div key={i} className={`chat__item chat__item--${m.role}`}>
                <div className={`chat__bubble chat__bubble--${m.role}${m.isError ? ' chat__bubble--error' : ''}`}>{m.text}</div>
                {m.products && m.products.length > 0 && (
                  <ul className="chat__products">
                    {m.products.map((p) => (
                      <li key={p.product_id}>
                        <Link to={`/products/${p.product_id}`} className="chat__product">
                          <img src={p.image_url} alt="" />
                          <span className="chat__product-name">{p.name}</span>
                          <span className="chat__product-price">{formatPrice(p.price)}</span>
                          <span className="chat__product-info">{p.short_info}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
            {pending && (
              <div className="chat__item chat__item--assistant">
                <div className="chat__bubble chat__bubble--assistant chat__typing" role="status" aria-label="The assistant is working on your answer">
                  <span className="chat__notes" aria-hidden="true">
                    <i>&#9834;</i>
                    <i>&#9835;</i>
                    <i>&#9834;</i>
                  </span>
                  <span className="chat__thinking">{THINKING_LINES[thinking]}</span>
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>
          {messages.length === 0 && !pending && (
            <div className="chat__starters" aria-label="Quick questions">
              {STARTERS.map((st) => (
                <button key={st.label} type="button" className="chat__starter" onClick={() => void send(st.text)}>
                  <span aria-hidden="true">&#9733;</span> {st.label}
                </button>
              ))}
            </div>
          )}
          <form className="chat__form" onSubmit={handleSubmit}>
            <textarea
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me about Yale gear, friend..."
              rows={1}
              maxLength={1000}
              aria-label="Message"
            />
            <button type="submit" className="btn btn--solid btn--small" disabled={!draft.trim() || pending}>
              Send
            </button>
          </form>
        </section>
      )}
      <button type="button" className="chat__toggle" onClick={() => setOpen((o) => !o)} aria-expanded={open}>
        <SaxIcon size={20} />
        <span>{open ? 'Close' : 'Personal Assistant'}</span>
        <span className="chat__toggle-notes" aria-hidden="true">
          <i>&#9834;</i>
          <i>&#9835;</i>
        </span>
      </button>
    </div>
  )
}

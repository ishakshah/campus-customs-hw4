import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { formatPrice, getProducts } from '../api'
import { aboutContent } from '../content'
import type { Product } from '../types'

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

/** Counts up to `target` the first time it scrolls into view (or just shows it, if motion is reduced). */
function CountUp({ target }: { target: number }) {
  const ref = useRef<HTMLSpanElement>(null)
  const [value, setValue] = useState(target)

  useEffect(() => {
    const el = ref.current
    if (!el || prefersReducedMotion() || typeof IntersectionObserver === 'undefined') return
    let frame = 0
    setValue(0)
    const observer = new IntersectionObserver(([entry]) => {
      if (!entry.isIntersecting) return
      observer.disconnect()
      const start = performance.now()
      const tick = (now: number) => {
        const progress = Math.min((now - start) / 1100, 1)
        setValue(Math.round(target * (1 - Math.pow(1 - progress, 3))))
        if (progress < 1) frame = requestAnimationFrame(tick)
      }
      frame = requestAnimationFrame(tick)
    })
    observer.observe(el)
    // Never leave the number stuck at 0 (for example if the page is opened in a background tab).
    const fallback = window.setTimeout(() => setValue(target), 4000)
    return () => {
      observer.disconnect()
      cancelAnimationFrame(frame)
      window.clearTimeout(fallback)
    }
  }, [target])

  return <span ref={ref}>{value}</span>
}

/** How many of `words` show up in at least one product name. */
const countMentioned = (products: Product[], words: string[]) =>
  words.filter((w) => products.some((p) => p.name.toLowerCase().includes(w.toLowerCase()))).length

export default function About() {
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    getProducts().then(setProducts).catch(() => setProducts([]))
  }, [])

  const collage = useMemo(
    () => aboutContent.collage.map((id) => products.find((p) => p.product_id === id)).filter((p): p is Product => p !== undefined),
    [products],
  )

  // Numbers come from the live catalogue, so they stay true when products change.
  const stats = useMemo(
    () => [
      { label: 'Styles', value: products.length },
      { label: 'Item types', value: new Set(products.map((p) => p.category)).size },
      { label: 'Residential colleges', value: countMentioned(products, aboutContent.colleges) },
      { label: 'Sports', value: countMentioned(products, aboutContent.sports) },
    ],
    [products],
  )

  return (
    <div className="about">
      <section className="about-hero">
        <div className="container about-hero__inner">
          <div className="about-hero__text">
            <p className="eyebrow">{aboutContent.eyebrow}</p>
            <h1>{aboutContent.headline}</h1>
            <p className="about-hero__lead">{aboutContent.intro}</p>
          </div>
          {collage.length > 0 && (
            <ul className="about-collage" aria-label="A few of our favorites">
              {collage.map((p, i) => (
                <li key={p.product_id} className={`about-collage__item about-collage__item--${i + 1}`}>
                  <Link to={`/products/${p.product_id}`} title={`${p.name}, ${formatPrice(p.price)}`}>
                    <img src={p.image_url} alt={p.name} />
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>

      <section className="container about-story">
        <div className="about-story__statement">
          <span className="about-story__mark" aria-hidden="true">
            &#9733;
          </span>
          <p>{aboutContent.statement}</p>
        </div>
        <div className="about-story__text">
          <h2>{aboutContent.storyHeading}</h2>
          {aboutContent.paragraphs.map((text) => (
            <p key={text}>{text}</p>
          ))}
        </div>
      </section>

      <section className="about-values">
        <div className="container">
          <h2 className="about-section-title">{aboutContent.valuesHeading}</h2>
          <div className="about-values__grid">
            {aboutContent.values.map((v, i) => (
              <article key={v.title} className="about-value">
                <span className="about-value__number" aria-hidden="true">
                  {String(i + 1).padStart(2, '0')}
                </span>
                <h3>{v.title}</h3>
                <p>{v.body}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      {products.length > 0 && (
        <section className="about-stats" aria-label="Campus Customs by the numbers">
          <div className="container about-stats__grid">
            {stats.map((s) => (
              <div key={s.label} className="about-stat">
                <strong>
                  <CountUp target={s.value} />
                </strong>
                <span>{s.label}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="container about-steps">
        <h2 className="about-section-title">{aboutContent.stepsHeading}</h2>
        <ol className="about-steps__list">
          {aboutContent.steps.map((step, i) => (
            <li key={step.title}>
              <span className="about-steps__badge" aria-hidden="true">
                {i + 1}
              </span>
              <div>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>

      <section className="about-cta">
        <div className="container about-cta__inner">
          <h2>{aboutContent.ctaHeading}</h2>
          <p>{aboutContent.ctaBody}</p>
          <div className="about-cta__actions">
            <Link to="/products" className="btn btn--light">
              Browse the collection
            </Link>
            <button type="button" className="btn btn--ghost" onClick={() => window.dispatchEvent(new Event('open-assistant'))}>
              Ask the assistant
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

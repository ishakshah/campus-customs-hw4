import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { formatPrice, getProducts } from '../api'
import CampusMap from '../components/CampusMap'
import { EXPLORE_SPOTS, creditUrl, photoUrl, thumbUrl } from '../explore'
import type { Product } from '../types'

const AUTOPLAY_MS = 6500
const SWIPE_PX = 50

const prefersReducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches

/** The item to wear at this stop: a photo, name, and price that link to the product page, plus sizes in stock. */
function Outfit({ product }: { product: Product }) {
  return (
    <Link to={`/products/${product.product_id}`} className="explore-outfit">
      <img src={product.image_url} alt={product.name} />
      <span className="explore-outfit__text">
        <span className="explore-outfit__label">Wear this</span>
        <strong>{product.name}</strong>
        <span className="explore-outfit__price">{formatPrice(product.price)}</span>
        <span className="explore-outfit__sizes">
          {product.available_sizes.length > 0 ? `In stock: ${product.available_sizes.join(' ')}` : 'Currently sold out'}
        </span>
      </span>
      <span className="explore-outfit__go" aria-hidden="true">
        Shop the look &rarr;
      </span>
    </Link>
  )
}

export default function Explore() {
  const [params, setParams] = useSearchParams()
  const total = EXPLORE_SPOTS.length
  const startIndex = Math.max(0, EXPLORE_SPOTS.findIndex((s) => s.id === params.get('stop')))
  const [index, setIndex] = useState(startIndex)
  const [playing, setPlaying] = useState(false)
  const [paused, setPaused] = useState(false) // true while the shopper is hovering or focused on the slideshow
  const [products, setProducts] = useState<Product[]>([])
  const swipeStart = useRef<number | null>(null)

  useEffect(() => {
    getProducts().then(setProducts).catch(() => setProducts([]))
  }, [])

  const spot = EXPLORE_SPOTS[index]
  const outfit = useMemo(() => products.find((p) => p.product_id === spot.productId), [products, spot])

  const go = useCallback((next: number) => setIndex(((next % total) + total) % total), [total])
  const prev = useCallback(() => go(index - 1), [go, index])
  const next = useCallback(() => go(index + 1), [go, index])

  // Keep the address in sync, so a stop can be shared as a link.
  useEffect(() => {
    setParams({ stop: spot.id }, { replace: true })
  }, [spot.id, setParams])

  // Arrow keys move through the slideshow (unless the shopper is typing somewhere).
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const target = e.target instanceof Element ? e.target : null
      if (target?.closest('input, textarea, select') || e.metaKey || e.ctrlKey || e.altKey) return
      if (e.key === 'ArrowRight') next()
      if (e.key === 'ArrowLeft') prev()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [next, prev])

  // Optional autoplay: off until the shopper turns it on, and paused while they are looking closely.
  useEffect(() => {
    if (!playing || paused || prefersReducedMotion()) return
    const timer = window.setTimeout(next, AUTOPLAY_MS)
    return () => window.clearTimeout(timer)
  }, [playing, paused, next])

  // Load the neighboring photos ahead of time, so clicking through feels instant.
  useEffect(() => {
    for (const offset of [-1, 1, 2]) new Image().src = photoUrl(EXPLORE_SPOTS[(index + offset + total) % total])
  }, [index, total])

  const surprise = () => {
    let pick = index
    while (pick === index) pick = Math.floor(Math.random() * total)
    go(pick)
  }

  return (
    <div className="explore">
      <section className="explore-hero">
        <div className="container explore-hero__inner">
          <div>
            <p className="eyebrow">Explore</p>
            <h1>Where will you wear it?</h1>
            <p className="explore-hero__lead">
              {total} iconic spots on and around the Yale campus, each with one piece from our collection to wear there.
              Click through the tour, or let us surprise you.
            </p>
          </div>
          <button type="button" className="btn btn--light" onClick={surprise}>
            &#9733; Surprise me
          </button>
        </div>
      </section>

      <div className="explore-layout">
      <section
        className="explore-show"
        role="region"
        aria-roledescription="carousel"
        aria-label="Tour of Yale campus"
        onMouseEnter={() => setPaused(true)}
        onMouseLeave={() => setPaused(false)}
        onFocus={() => setPaused(true)}
        onBlur={() => setPaused(false)}
      >
        <p className="visually-hidden" role="status" aria-live="polite">
          Stop {index + 1} of {total}: {spot.name}
        </p>

        <div
          className="explore-stage"
          onPointerDown={(e) => {
            swipeStart.current = e.clientX
          }}
          onPointerUp={(e) => {
            if (swipeStart.current === null) return
            const dx = e.clientX - swipeStart.current
            swipeStart.current = null
            if (dx > SWIPE_PX) prev()
            else if (dx < -SWIPE_PX) next()
          }}
        >
          <img key={spot.id} className="explore-stage__photo" src={photoUrl(spot)} alt={`${spot.name}, Yale`} draggable={false} />
          <button type="button" className="explore-arrow explore-arrow--prev" onClick={prev} aria-label="Previous stop">
            &#8249;
          </button>
          <button type="button" className="explore-arrow explore-arrow--next" onClick={next} aria-label="Next stop">
            &#8250;
          </button>
          <span className="explore-stage__count" aria-hidden="true">
            {String(index + 1).padStart(2, '0')} / {total}
          </span>
          <button
            type="button"
            className="explore-play"
            onClick={() => setPlaying((p) => !p)}
            aria-pressed={playing}
            aria-label={playing ? 'Pause the slideshow' : 'Play the slideshow automatically'}
          >
            {playing ? '❚❚ Pause' : '▶ Play'}
          </button>
        </div>

        <p className="explore-credit">
          Photo: {spot.credit.author} &middot; {spot.credit.license} &middot;{' '}
          <a href={creditUrl(spot.credit)} target="_blank" rel="noreferrer">
            Wikimedia Commons
          </a>
        </p>

        <div className="explore-info">
          <div className="explore-info__text">
            <p className="explore-info__stop">
              Stop {String(index + 1).padStart(2, '0')} of {total}
              <span className={`explore-tag explore-tag--${spot.category.replace(/\s/g, '').toLowerCase()}`}>{spot.category}</span>
            </p>
            <h2>{spot.name}</h2>
            <p>{spot.about}</p>
            <p className="explore-info__why">{spot.why}</p>
          </div>
          {outfit && <Outfit product={outfit} />}
        </div>

        <ol className="explore-thumbs" aria-label="All stops">
          {EXPLORE_SPOTS.map((s, i) => (
            <li key={s.id}>
              <button
                type="button"
                className={`explore-thumb${i === index ? ' is-on' : ''}`}
                onClick={() => go(i)}
                aria-label={`Go to stop ${i + 1}: ${s.name}`}
                aria-current={i === index}
              >
                <img src={thumbUrl(s)} alt="" loading="lazy" />
                <span>{i + 1}</span>
              </button>
            </li>
          ))}
        </ol>
      </section>

      <aside className="explore-map" aria-label="Campus map">
        <CampusMap activeIndex={index} onSelect={go} />
      </aside>
      </div>
    </div>
  )
}

import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fitDescription, formatPrice, getProducts } from '../api'
import ProductFilters from '../components/ProductFilters'
import { useSearchResults } from '../ResultsContext'
import {
  SORT_OPTIONS,
  activeFilterCount,
  byAvailability,
  describeAssistantFilters,
  describeAssistantSort,
  filterProducts,
  filtersFromAssistant,
  sortProducts,
} from '../shopFilters'
import type { Filters, SortKey } from '../shopFilters'
import type { PageFilters, Product } from '../types'

interface BrowserProps {
  /** The products to browse, already in relevance order (most relevant first). */
  base: Product[]
  /** Short info lines for assistant search results, by product id. Shown under the price when present. */
  shortInfo?: Map<string, string>
  /** Filters the assistant switched on for these results, if any. */
  assistantFilters?: PageFilters | null
}

function ProductBrowser({ base, shortInfo, assistantFilters = null }: BrowserProps) {
  const start = filtersFromAssistant(assistantFilters)
  const [filters, setFilters] = useState<Filters>(start.filters)
  const [sort, setSort] = useState<SortKey>(start.sort)
  const [filtersOpen, setFiltersOpen] = useState(false) // small screens only

  const shown = useMemo(() => sortProducts(filterProducts(base, filters), sort), [base, filters, sort])
  const active = activeFilterCount(filters)

  return (
    <div className="shop">
      <aside className={`shop__filters${filtersOpen ? ' is-open' : ''}`} aria-label="Product filters">
        <ProductFilters products={base} filters={filters} onChange={setFilters} />
      </aside>

      <div className="shop__main">
        <div className="shop__toolbar">
          <button type="button" className="btn btn--outline btn--small shop__filters-toggle" aria-expanded={filtersOpen} onClick={() => setFiltersOpen((o) => !o)}>
            {filtersOpen ? 'Hide filters' : `Filters${active ? ` (${active})` : ''}`}
          </button>
          <p className="shop__count" role="status" aria-live="polite">
            Showing <strong>{shown.length}</strong> of {base.length} products
          </p>
          <label className="shop__sort">
            <span>Sort by</span>
            <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
              {SORT_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        {shown.length === 0 ? (
          <div className="placeholder">
            No products match these filters.{' '}
            <button type="button" className="link-button" onClick={() => setFilters(filtersFromAssistant(null).filters)}>
              Clear all filters
            </button>
          </div>
        ) : (
          <div className="product-grid">
            {shown.map((p) => {
              const info = shortInfo?.get(p.product_id)
              return (
                <Link key={p.product_id} to={`/products/${p.product_id}`} className="product-card">
                  <div className="product-card__image">
                    <img src={p.image_url} alt={p.name} loading="lazy" />
                    {!info && <p className="product-card__overlay">{fitDescription(p.description)}</p>}
                  </div>
                  <div className="product-card__body">
                    <h3>{p.name}</h3>
                    <p className="product-card__price">{formatPrice(p.price)}</p>
                    {info && <p className="product-card__info">{info}</p>}
                  </div>
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default function Products() {
  const { results, clearResults } = useSearchResults()
  const [products, setProducts] = useState<Product[] | null>(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    getProducts().then(setProducts).catch(() => setError(true))
  }, [])

  // New results from the Personal Assistant: bring them into view.
  useEffect(() => {
    if (results) window.scrollTo({ top: 0, behavior: 'smooth' })
  }, [results])

  // The products to browse, in relevance order: the assistant's ranking for its results, otherwise the products
  // that are available in the most sizes.
  const view = useMemo(() => {
    if (!products) return null
    if (!results) return { base: byAvailability(products), shortInfo: undefined, assistantFilters: null, key: 'all' }
    const byId = new Map(products.map((p) => [p.product_id, p]))
    const base = results.products.map((c) => byId.get(c.product_id)).filter((p): p is Product => p !== undefined)
    const shortInfo = new Map(results.products.map((c) => [c.product_id, c.short_info]))
    return {
      base,
      shortInfo,
      assistantFilters: results.filters,
      key: `${results.title}|${results.total}|${results.products[0]?.product_id ?? ''}|${JSON.stringify(results.filters)}`,
    }
  }, [products, results])

  return (
    <section className="container page">
      <h1>Products</h1>
      {results ? (
        <div className="results-banner" role="status">
          <p>
            Results for <strong>{results.title}</strong>, found by your Personal Assistant.
            {describeAssistantFilters(results.filters) && (
              <>
                {' '}
                Filters it turned on: <strong>{describeAssistantFilters(results.filters)}</strong>. You can change them in the filter panel.
              </>
            )}
            {describeAssistantSort(results.filters) && (
              <>
                {' '}
                Sorted by <strong>{describeAssistantSort(results.filters).toLowerCase()}</strong>.
              </>
            )}
          </p>
          <button type="button" className="btn btn--outline btn--small" onClick={clearResults}>
            Show all products
          </button>
        </div>
      ) : (
        <p className="lead">Browse our collection of Yale apparel.</p>
      )}
      {error && <div className="placeholder">We couldn't load the products. Please try again shortly.</div>}
      {!error && !view && <div className="placeholder">Loading products...</div>}
      {/* New key = fresh filters, so a new assistant search never starts with old filters hiding its results. */}
      {view && <ProductBrowser key={view.key} base={view.base} shortInfo={view.shortInfo} assistantFilters={view.assistantFilters} />}
    </section>
  )
}

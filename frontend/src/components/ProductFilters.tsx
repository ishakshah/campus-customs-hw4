import type { Filters } from '../shopFilters'
import { SIZES, activeFilterCount, countOptions } from '../shopFilters'
import type { Product } from '../types'

interface Props {
  /** Every product the filters apply to, before any filtering (used for the option counts). */
  products: Product[]
  filters: Filters
  onChange: (filters: Filters) => void
}

const SWATCHES: Record<string, string> = {
  Navy: '#1c2f5a',
  Blue: '#2f6fd0',
  Gray: '#9aa0a6',
  White: '#ffffff',
  Cream: '#f3ead3',
  Red: '#c0392b',
  Black: '#111111',
  'Gold / Yellow': '#d4a017',
  Green: '#2e7d32',
  Coral: '#e07a5f',
  Multicolor: 'conic-gradient(#c0392b, #d4a017, #2e7d32, #2f6fd0, #c0392b)',
}

const toggle = (list: string[], value: string) => (list.includes(value) ? list.filter((v) => v !== value) : [...list, value])

export default function ProductFilters({ products, filters, onChange }: Props) {
  const categoryCounts = countOptions(products, filters, 'categories')
  const sizeCounts = countOptions(products, filters, 'sizes')
  const colorCounts = countOptions(products, filters, 'colors')
  // Show every option that exists in this set of products, so options do not jump around as filters change.
  const categories = [...new Set(products.map((p) => p.category))].sort()
  const colors = [...new Set(products.map((p) => p.primary_color).filter(Boolean))].sort()
  const prices = products.map((p) => p.price)
  const lowest = prices.length ? Math.min(...prices) : 0
  const highest = prices.length ? Math.max(...prices) : 0
  const count = activeFilterCount(filters)

  return (
    <div className="filters">
      <div className="filters__head">
        <h2>Filters</h2>
        {count > 0 && (
          <button type="button" className="link-button" onClick={() => onChange({ categories: [], sizes: [], colors: [], minPrice: '', maxPrice: '' })}>
            Clear all ({count})
          </button>
        )}
      </div>

      <fieldset className="filters__group">
        <legend>Item type</legend>
        {categories.map((c) => {
          const n = categoryCounts.get(c) ?? 0
          return (
            <label key={c} className={`filters__option${n === 0 && !filters.categories.includes(c) ? ' is-empty' : ''}`}>
              <input type="checkbox" checked={filters.categories.includes(c)} onChange={() => onChange({ ...filters, categories: toggle(filters.categories, c) })} />
              <span>{c}</span>
              <span className="filters__count">{n}</span>
            </label>
          )
        })}
      </fieldset>

      <fieldset className="filters__group">
        <legend>Size (in stock)</legend>
        <div className="filters__sizes">
          {SIZES.map((s) => {
            const n = sizeCounts.get(s) ?? 0
            const on = filters.sizes.includes(s)
            return (
              <button
                key={s}
                type="button"
                className={`size-toggle${on ? ' is-on' : ''}${n === 0 && !on ? ' is-empty' : ''}`}
                aria-pressed={on}
                title={`${n} product${n === 1 ? '' : 's'} in stock in ${s}`}
                onClick={() => onChange({ ...filters, sizes: toggle(filters.sizes, s) })}
              >
                {s}
              </button>
            )
          })}
        </div>
      </fieldset>

      <fieldset className="filters__group">
        <legend>Color</legend>
        {colors.map((c) => {
          const n = colorCounts.get(c) ?? 0
          return (
            <label key={c} className={`filters__option${n === 0 && !filters.colors.includes(c) ? ' is-empty' : ''}`}>
              <input type="checkbox" checked={filters.colors.includes(c)} onChange={() => onChange({ ...filters, colors: toggle(filters.colors, c) })} />
              <span className="swatch" style={{ background: SWATCHES[c] ?? '#ccc' }} aria-hidden="true" />
              <span>{c}</span>
              <span className="filters__count">{n}</span>
            </label>
          )
        })}
      </fieldset>

      <fieldset className="filters__group">
        <legend>Price</legend>
        <div className="filters__price">
          <label>
            <span className="visually-hidden">Minimum price</span>
            <span className="filters__money">$</span>
            <input type="number" inputMode="decimal" min="0" step="1" placeholder={String(Math.floor(lowest))} value={filters.minPrice} onChange={(e) => onChange({ ...filters, minPrice: e.target.value })} />
          </label>
          <span aria-hidden="true">to</span>
          <label>
            <span className="visually-hidden">Maximum price</span>
            <span className="filters__money">$</span>
            <input type="number" inputMode="decimal" min="0" step="1" placeholder={String(Math.ceil(highest))} value={filters.maxPrice} onChange={(e) => onChange({ ...filters, maxPrice: e.target.value })} />
          </label>
        </div>
        <p className="filters__hint">
          Prices here run from ${Math.floor(lowest)} to ${Math.ceil(highest)}.
        </p>
      </fieldset>
    </div>
  )
}

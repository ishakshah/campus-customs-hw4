import type { PageFilters, Product } from './types'

export const SIZES = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

export interface Filters {
  categories: string[]
  sizes: string[]
  colors: string[]
  minPrice: string
  maxPrice: string
}

export const NO_FILTERS: Filters = { categories: [], sizes: [], colors: [], minPrice: '', maxPrice: '' }

export type Facet = 'categories' | 'sizes' | 'colors' | 'price'

export type SortKey = 'relevance-desc' | 'relevance-asc' | 'price-desc' | 'price-asc' | 'name-asc' | 'name-desc'

export const SORT_OPTIONS: { value: SortKey; label: string }[] = [
  { value: 'relevance-desc', label: 'Relevance: most to least' },
  { value: 'relevance-asc', label: 'Relevance: least to most' },
  { value: 'price-desc', label: 'Price: high to low' },
  { value: 'price-asc', label: 'Price: low to high' },
  { value: 'name-asc', label: 'Alphabetical: A to Z' },
  { value: 'name-desc', label: 'Alphabetical: Z to A' },
]

const parsePrice = (text: string): number | null => {
  if (text.trim() === '') return null
  const value = Number(text)
  return Number.isFinite(value) ? value : null
}

export function activeFilterCount(f: Filters): number {
  const priceActive = parsePrice(f.minPrice) !== null || parsePrice(f.maxPrice) !== null
  return f.categories.length + f.sizes.length + f.colors.length + (priceActive ? 1 : 0)
}

/** Does a product pass the filters? `skip` leaves one group out (used to count the options in that group). */
export function matchesFilters(p: Product, f: Filters, skip?: Facet): boolean {
  if (skip !== 'categories' && f.categories.length > 0 && !f.categories.includes(p.category)) return false
  // Sizes: in stock in at least one of the chosen sizes.
  if (skip !== 'sizes' && f.sizes.length > 0 && !f.sizes.some((s) => p.available_sizes.includes(s))) return false
  // Colors: the product's one primary color is one of the chosen colors (its accent colors do not count).
  if (skip !== 'colors' && f.colors.length > 0 && !f.colors.includes(p.primary_color)) return false
  if (skip !== 'price') {
    const min = parsePrice(f.minPrice)
    const max = parsePrice(f.maxPrice)
    if (min !== null && p.price < min) return false
    if (max !== null && p.price > max) return false
  }
  return true
}

export const filterProducts = (products: Product[], f: Filters) => products.filter((p) => matchesFilters(p, f))

/** How many products each option would show, given the other filters that are already on. */
export function countOptions(products: Product[], f: Filters, facet: Exclude<Facet, 'price'>): Map<string, number> {
  const counts = new Map<string, number>()
  for (const p of products) {
    if (!matchesFilters(p, f, facet)) continue
    const values = facet === 'categories' ? [p.category] : facet === 'sizes' ? p.available_sizes : [p.primary_color]
    for (const v of values) counts.set(v, (counts.get(v) ?? 0) + 1)
  }
  return counts
}

/** `products` must already be in relevance order (most relevant first). Ties keep that order. */
export function sortProducts(products: Product[], key: SortKey): Product[] {
  const list = [...products]
  switch (key) {
    case 'relevance-desc':
      return list
    case 'relevance-asc':
      return list.reverse()
    case 'price-desc':
      return list.sort((a, b) => b.price - a.price)
    case 'price-asc':
      return list.sort((a, b) => a.price - b.price)
    case 'name-asc':
      return list.sort((a, b) => a.name.localeCompare(b.name))
    case 'name-desc':
      return list.sort((a, b) => b.name.localeCompare(a.name))
  }
}

/** Relevance for the full catalogue: products you can buy in more sizes come first, then A to Z. */
export const byAvailability = (products: Product[]): Product[] =>
  [...products].sort((a, b) => b.available_sizes.length - a.available_sizes.length || a.name.localeCompare(b.name))

/** Turn the filters the assistant chose into the page's filter state. */
export function filtersFromAssistant(f: PageFilters | null): { filters: Filters; sort: SortKey } {
  if (!f) return { filters: NO_FILTERS, sort: 'relevance-desc' }
  return {
    filters: {
      categories: f.categories,
      sizes: f.sizes,
      colors: f.colors,
      minPrice: f.min_price === null ? '' : String(f.min_price),
      maxPrice: f.max_price === null ? '' : String(f.max_price),
    },
    sort: f.sort ?? 'relevance-desc',
  }
}

/** A short description of the filters the assistant turned on, for the banner, e.g. "Size M, Navy, up to $60". */
export function describeAssistantFilters(f: PageFilters | null): string {
  if (!f) return ''
  const parts: string[] = []
  if (f.categories.length) parts.push(f.categories.join(' or '))
  if (f.sizes.length) parts.push(`Size ${f.sizes.join(' or ')}`)
  if (f.colors.length) parts.push(f.colors.join(' or '))
  if (f.min_price !== null && f.max_price !== null) parts.push(`$${f.min_price} to $${f.max_price}`)
  else if (f.max_price !== null) parts.push(`up to $${f.max_price}`)
  else if (f.min_price !== null) parts.push(`$${f.min_price} and up`)
  return parts.join(', ')
}

/** The sort order the assistant chose, for the banner, e.g. "Price: low to high". */
export const describeAssistantSort = (f: PageFilters | null): string => SORT_OPTIONS.find((o) => o.value === f?.sort)?.label ?? ''


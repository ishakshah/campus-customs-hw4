export interface Product {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  category: string
  primary_color: string
  available_sizes: string[]
}

export interface SizeStock {
  size: string
  quantity: number
}

export interface ProductDetail extends Product {
  sizes: SizeStock[]
}

export interface User {
  id: number
  first_name: string
  last_name: string
  email: string
}

export interface RegisterInput {
  first_name: string
  last_name: string
  email: string
  password: string
  confirm_password: string
}

export interface ProductCard {
  product_id: string
  name: string
  price: number
  image_url: string
  short_info: string
}

/** Filters (and a sort order) the assistant switches on for the shopper on the Products page. */
export interface PageFilters {
  categories: string[]
  sizes: string[]
  colors: string[]
  min_price: number | null
  max_price: number | null
  sort: 'relevance-desc' | 'relevance-asc' | 'price-desc' | 'price-asc' | 'name-asc' | 'name-desc' | null
}

export interface SearchResults {
  title: string
  total: number
  products: ProductCard[]
  filters: PageFilters | null
}

export interface ChatReply {
  message: string
  products: ProductCard[]
  results: SearchResults | null
}

export interface StoredMessage {
  role: 'user' | 'assistant'
  content: string
  products: ProductCard[]
}

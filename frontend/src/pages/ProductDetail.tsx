import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { formatPrice, getProduct, NO_DESCRIPTION } from '../api'
import type { ProductDetail as ProductDetailType } from '../types'

const LOW_STOCK = 5

function stockLabel(quantity: number) {
  if (quantity === 0) return 'Sold out'
  if (quantity <= LOW_STOCK) return `Only ${quantity} left`
  return `${quantity} in stock`
}

// Keyed by productId so navigating between products resets the loading state.
export default function ProductDetail() {
  const { productId = '' } = useParams()
  return <ProductView key={productId} productId={productId} />
}

function ProductView({ productId }: { productId: string }) {
  const [product, setProduct] = useState<ProductDetailType | null>(null)
  const [status, setStatus] = useState<'loading' | 'ready' | 'not-found' | 'error'>('loading')

  useEffect(() => {
    getProduct(productId)
      .then((p) => {
        setProduct(p)
        setStatus('ready')
      })
      .catch((e: Error) => setStatus(e.message === 'not-found' ? 'not-found' : 'error'))
  }, [productId])

  return (
    <section className="container page">
      <Link to="/products" className="back-link">
        &larr; All products
      </Link>
      {status === 'loading' && <div className="placeholder">Loading product...</div>}
      {status === 'not-found' && <div className="placeholder">We couldn't find that product.</div>}
      {status === 'error' && <div className="placeholder">We couldn't load this product. Please try again shortly.</div>}
      {status === 'ready' && product && (
        <div className="product-detail">
          <div className="product-detail__image">
            <img src={product.image_url} alt={product.name} />
          </div>
          <div className="product-detail__info">
            <p className="eyebrow eyebrow--dark">{product.garment_type}</p>
            <h1>{product.name}</h1>
            <p className="product-detail__price">{formatPrice(product.price)}</p>
            <p className="product-detail__desc">{product.description || NO_DESCRIPTION}</p>
            {product.colors.length > 0 && (
              <>
                <h2 className="detail-heading">Colors</h2>
                <p>{product.colors.join(', ')}</p>
              </>
            )}
            <h2 className="detail-heading">Sizes &amp; availability</h2>
            <ul className="size-list">
              {product.sizes.map((s) => (
                <li key={s.size} className={`size-chip${s.quantity === 0 ? ' size-chip--out' : ''}`}>
                  <span className="size-chip__size">{s.size}</span>
                  <span className="size-chip__stock">{stockLabel(s.quantity)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  )
}

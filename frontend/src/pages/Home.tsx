import { Link } from 'react-router-dom'
import { homeContent } from '../content'

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="container hero__inner">
          <p className="eyebrow">{homeContent.eyebrow}</p>
          <h1>{homeContent.headline}</h1>
          <p className="hero__sub">{homeContent.subhead}</p>
          <div className="hero__actions">
            <Link to="/products" className="btn btn--light">
              {homeContent.primaryCta}
            </Link>
            <Link to="/about" className="btn btn--ghost">
              {homeContent.secondaryCta}
            </Link>
          </div>
        </div>
      </section>
      <nav className="container category-strip" aria-label="Shop by category">
        {homeContent.categories.map((label) => (
          <Link key={label} to="/products" className="category-chip">
            {label}
          </Link>
        ))}
      </nav>
      <section className="container highlights">
        {homeContent.highlights.map((item) => (
          <article key={item.title} className="card">
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </article>
        ))}
      </section>
    </>
  )
}

import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import { useSearchResults } from '../ResultsContext'

const pageLinks = [
  { to: '/', label: 'Home', end: true },
  { to: '/products', label: 'Products' },
  { to: '/explore', label: 'Explore' },
  { to: '/about', label: 'About Us' },
]

export default function NavBar() {
  const { user, loading, logout } = useAuth()
  const { clearResults } = useSearchResults()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <header className="navbar">
      <div className="navbar__inner">
        <Link to="/" className="navbar__brand">
          Campus Customs
        </Link>
        <nav className="navbar__links" aria-label="Main">
          {pageLinks.map(({ to, label, end }) => (
            <NavLink key={to} to={to} end={end} className="navbar__link" onClick={to === '/products' ? clearResults : undefined}>
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="navbar__account">
          {loading ? null : user ? (
            <>
              <span className="navbar__greeting">Hi, {user.first_name}</span>
              <button type="button" className="btn btn--outline btn--small" onClick={handleLogout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="navbar__link">
                Log in
              </NavLink>
              <NavLink to="/create-account" className="btn btn--solid btn--small">
                Create account
              </NavLink>
            </>
          )}
        </div>
      </div>
    </header>
  )
}

import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../AuthContext'

/** A reminder across the whole site while the signed-in shopper's password still needs updating. */
export default function PasswordBanner() {
  const { user, passwordUpdateRequired } = useAuth()
  const { pathname } = useLocation()
  if (!user || !passwordUpdateRequired || pathname === '/update-password') return null
  return (
    <div className="password-banner" role="status">
      <p>
        Your password doesn't meet our new security requirements (10+ characters with a letter, a number, and a special character).{' '}
        <Link to="/update-password">Update your password</Link>
      </p>
    </div>
  )
}

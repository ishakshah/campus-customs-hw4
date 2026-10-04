import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import PasswordChecklist from '../components/PasswordChecklist'
import { MAX_PASSWORD_LENGTH, passwordIsValid } from '../passwordRules'

export default function UpdatePassword() {
  const { user, loading, passwordUpdateRequired, changePassword } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ current: '', next: '', confirm: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (loading) return null
  if (!user) return <Navigate to="/login" replace />

  const set = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))
  const mismatch = form.confirm !== '' && form.next !== form.confirm

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (!passwordIsValid(form.next)) {
      setError('Please choose a password that meets all the requirements listed below the new password field.')
      return
    }
    if (form.next !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await changePassword(form.current, form.next, form.confirm)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
      setSubmitting(false)
    }
  }

  return (
    <section className="container page page--narrow">
      <h1>Update your password</h1>
      {passwordUpdateRequired ? (
        <p className="lead">
          Your password doesn't meet our new security requirements. Please choose a new one to keep your account safe.
        </p>
      ) : (
        <p className="lead">Choose a new password for your account.</p>
      )}
      <form className="form" onSubmit={handleSubmit}>
        {error && (
          <p className="form__error" role="alert">
            {error}
          </p>
        )}
        <label>
          Current password
          <input type="password" name="current_password" autoComplete="current-password" required value={form.current} onChange={set('current')} />
        </label>
        <label>
          New password
          <input
            type="password"
            name="new_password"
            autoComplete="new-password"
            required
            maxLength={MAX_PASSWORD_LENGTH}
            aria-describedby="update-password-rules"
            value={form.next}
            onChange={set('next')}
          />
          <PasswordChecklist id="update-password-rules" password={form.next} />
        </label>
        <label>
          Confirm new password
          <input
            type="password"
            name="confirm_password"
            autoComplete="new-password"
            required
            maxLength={MAX_PASSWORD_LENGTH}
            aria-invalid={mismatch}
            value={form.confirm}
            onChange={set('confirm')}
          />
          {mismatch && <span className="form__hint form__hint--error">Passwords do not match.</span>}
        </label>
        <button type="submit" className="btn btn--solid" disabled={submitting}>
          {submitting ? 'Updating...' : 'Update password'}
        </button>
      </form>
      {passwordUpdateRequired && (
        <p className="muted">
          Not now? <Link to="/">Continue to the site</Link>. We'll keep reminding you until you update it.
        </p>
      )}
    </section>
  )
}

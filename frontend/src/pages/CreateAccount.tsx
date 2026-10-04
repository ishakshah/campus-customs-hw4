import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../AuthContext'
import PasswordChecklist from '../components/PasswordChecklist'
import { MAX_PASSWORD_LENGTH, passwordIsValid } from '../passwordRules'

export default function CreateAccount() {
  const { user, register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '', password: '', confirm_password: '' })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  const set = (field: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }))

  const mismatch = form.confirm_password !== '' && form.password !== form.confirm_password

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (!passwordIsValid(form.password)) {
      setError('Please choose a password that meets all the requirements listed below the password field.')
      return
    }
    if (form.password !== form.confirm_password) {
      setError('Passwords do not match.')
      return
    }
    setSubmitting(true)
    try {
      await register(form)
      navigate('/')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.')
      setSubmitting(false)
    }
  }

  return (
    <section className="container page page--narrow">
      <h1>Create account</h1>
      <form className="form" onSubmit={handleSubmit}>
        {error && (
          <p className="form__error" role="alert">
            {error}
          </p>
        )}
        <div className="form__row">
          <label>
            First name
            <input type="text" name="first_name" autoComplete="given-name" required maxLength={60} value={form.first_name} onChange={set('first_name')} />
          </label>
          <label>
            Last name
            <input type="text" name="last_name" autoComplete="family-name" required maxLength={60} value={form.last_name} onChange={set('last_name')} />
          </label>
        </div>
        <label>
          Email
          <input type="email" name="email" autoComplete="email" required value={form.email} onChange={set('email')} />
        </label>
        <label>
          Password
          <input
            type="password"
            name="password"
            autoComplete="new-password"
            required
            maxLength={MAX_PASSWORD_LENGTH}
            aria-describedby="password-rules"
            value={form.password}
            onChange={set('password')}
          />
          <PasswordChecklist id="password-rules" password={form.password} />
        </label>
        <label>
          Confirm password
          <input
            type="password"
            name="confirm_password"
            autoComplete="new-password"
            required
            maxLength={128}
            aria-invalid={mismatch}
            value={form.confirm_password}
            onChange={set('confirm_password')}
          />
          {mismatch && <span className="form__hint form__hint--error">Passwords do not match.</span>}
        </label>
        <button type="submit" className="btn btn--solid" disabled={submitting}>
          {submitting ? 'Creating account...' : 'Create account'}
        </button>
      </form>
      <p className="muted">
        Already have an account? <Link to="/login">Log in</Link>
      </p>
    </section>
  )
}

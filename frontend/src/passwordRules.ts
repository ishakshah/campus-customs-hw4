// New-password rules. The server enforces the same rules (backend/main.py, password_problems).
export const MIN_PASSWORD_LENGTH = 10
export const MAX_PASSWORD_LENGTH = 128

export interface PasswordRule {
  id: 'length' | 'letter' | 'number' | 'special'
  label: string
  met: boolean
}

export function passwordRules(password: string): PasswordRule[] {
  return [
    { id: 'length', label: `At least ${MIN_PASSWORD_LENGTH} characters`, met: password.length >= MIN_PASSWORD_LENGTH },
    { id: 'letter', label: 'A letter', met: /\p{L}/u.test(password) },
    { id: 'number', label: 'A number', met: /\p{Nd}/u.test(password) },
    { id: 'special', label: 'A special character (like ! ? # $ %)', met: /[^\p{L}\p{N}\s]/u.test(password) },
  ]
}

export const passwordIsValid = (password: string) =>
  password.length <= MAX_PASSWORD_LENGTH && passwordRules(password).every((rule) => rule.met)

import { passwordRules } from '../passwordRules'

/** The password requirements, ticking off as the shopper types. */
export default function PasswordChecklist({ password, id }: { password: string; id: string }) {
  return (
    <ul id={id} className="password-rules" aria-label="Password requirements">
      {passwordRules(password).map((rule) => (
        <li key={rule.id} className={rule.met ? 'is-met' : ''}>
          <span aria-hidden="true">{rule.met ? '\u2713' : '\u25CB'}</span>
          {rule.label}
          <span className="visually-hidden">{rule.met ? ' (done)' : ' (not yet)'}</span>
        </li>
      ))}
    </ul>
  )
}

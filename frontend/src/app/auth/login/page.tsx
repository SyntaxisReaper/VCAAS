import { redirect } from 'next/navigation'

/**
 * /auth/login is a legacy broken route that calls non-existent API endpoints.
 * Redirect permanently to the real login page at /login.
 */
export default function AuthLoginRedirect() {
  redirect('/login')
}
import { redirect } from 'next/navigation'

/**
 * /auth/signup is a legacy broken route that calls a non-existent /api/auth/signup endpoint.
 * It never touches Firebase and stores no user data.
 * Redirect permanently to the real signup page at /signup.
 */
export default function AuthSignupRedirect() {
  redirect('/signup')
}
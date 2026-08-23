'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { 
  EyeIcon, 
  EyeSlashIcon, 
  ShieldCheckIcon,
  KeyIcon,
  UserIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline'
import { adminAuth, useAdminAuth } from '@/lib/adminAuth'

export default function AdminLoginPage() {
  const router = useRouter()
  const { isAdmin, login } = useAdminAuth()
  const [credentials, setCredentials] = useState({
    username: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [attempts, setAttempts] = useState(0)
  const [isLocked, setIsLocked] = useState(false)
  const [lockoutTime, setLockoutTime] = useState(0)
  const [isClient, setIsClient] = useState(false)

  // Handle client-side mounting
  useEffect(() => {
    setIsClient(true)
  }, [])

  // Redirect if already authenticated
  useEffect(() => {
    if (!isClient) return // Wait for client-side hydration
    
    if (isAdmin) {
      router.push('/admin/dashboard')
    }
  }, [isAdmin, router, isClient])

  // Handle lockout timer
  useEffect(() => {
    let timer: NodeJS.Timeout
    if (isLocked && lockoutTime > 0) {
      timer = setInterval(() => {
        setLockoutTime(prev => {
          if (prev <= 1) {
            setIsLocked(false)
            setAttempts(0)
            return 0
          }
          return prev - 1
        })
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [isLocked, lockoutTime])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (isLocked) {
      setError(`Account locked. Try again in ${lockoutTime} seconds.`)
      return
    }

    if (!credentials.username.trim() || !credentials.password.trim()) {
      setError('Both username and password are required')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const session = await login(credentials.username, credentials.password)
      
      if (session) {
        // Success - redirect to admin dashboard
        console.log('🎉 Admin login successful')
        adminAuth.enableAdminFeatures()
        router.push('/admin/dashboard')
      } else {
        // Failed login
        const newAttempts = attempts + 1
        setAttempts(newAttempts)
        
        if (newAttempts >= 3) {
          setIsLocked(true)
          setLockoutTime(60) // 60 seconds lockout
          setError('Too many failed attempts. Account locked for 60 seconds.')
        } else {
          setError(`Invalid credentials. ${3 - newAttempts} attempts remaining.`)
        }
      }
    } catch (error) {
      setError('Authentication system error. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const formatLockoutTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return mins > 0 ? `${mins}:${secs.toString().padStart(2, '0')}` : `${secs}s`
  }

  if (!isClient) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-black flex items-center justify-center p-4">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-red-500 mx-auto mb-4"></div>
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-red-900 to-black flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/20 backdrop-blur-sm"></div>
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-red-600/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-600/20 rounded-full blur-3xl animate-pulse delay-700"></div>
      </div>

      <div className="relative w-full max-w-md">
        {/* Warning banner */}
        <div className="mb-6 p-4 bg-red-600/20 border border-red-500/30 rounded-lg backdrop-blur-sm">
          <div className="flex items-center text-red-300 text-sm">
            <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            <span>RESTRICTED ACCESS - Authorized Personnel Only</span>
          </div>
        </div>

        <div className="bg-gray-800/80 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-8 shadow-2xl">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-red-500 to-red-600 rounded-full mb-4">
              <ShieldCheckIcon className="h-8 w-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-white mb-2">Admin Access</h1>
            <p className="text-gray-400 text-sm">Enter your administrative credentials</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-6 p-4 bg-red-600/20 border border-red-500/30 rounded-lg">
              <div className="flex items-center text-red-300 text-sm">
                <ExclamationTriangleIcon className="h-5 w-5 mr-2 flex-shrink-0" />
                <span>{error}</span>
              </div>
            </div>
          )}

          {/* Lockout status */}
          {isLocked && (
            <div className="mb-6 p-4 bg-yellow-600/20 border border-yellow-500/30 rounded-lg">
              <div className="flex items-center text-yellow-300 text-sm">
                <KeyIcon className="h-5 w-5 mr-2 flex-shrink-0" />
                <span>Account locked for: {formatLockoutTime(lockoutTime)}</span>
              </div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Username field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Username
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <UserIcon className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials(prev => ({ ...prev, username: e.target.value }))}
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 focus:bg-gray-700 transition-all duration-200"
                  placeholder="Enter admin username"
                  disabled={isLoading || isLocked}
                  autoComplete="off"
                />
              </div>
            </div>

            {/* Password field */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <KeyIcon className="h-5 w-5 text-gray-500" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={credentials.password}
                  onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
                  className="w-full pl-10 pr-12 py-3 bg-gray-800 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-red-500 focus:bg-gray-700 transition-all duration-200"
                  placeholder="Enter admin password"
                  disabled={isLoading || isLocked}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  onClick={() => setShowPassword(!showPassword)}
                  disabled={isLoading || isLocked}
                >
                  {showPassword ? (
                    <EyeSlashIcon className="h-5 w-5 text-gray-500 hover:text-gray-400" />
                  ) : (
                    <EyeIcon className="h-5 w-5 text-gray-500 hover:text-gray-400" />
                  )}
                </button>
              </div>
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading || isLocked}
              className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 disabled:from-gray-600 disabled:to-gray-700 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 transform hover:scale-[1.02] disabled:scale-100 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 focus:ring-offset-gray-800"
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                  Authenticating...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  Access Admin Panel
                </div>
              )}
            </button>
          </form>

          {/* Security notice */}
          <div className="mt-8 p-4 bg-gray-700/30 rounded-lg border border-gray-600/30">
            <div className="text-xs text-gray-400 text-center space-y-1">
              <p>🔒 All access attempts are logged and monitored</p>
              <p>⚠️ Unauthorized access is strictly prohibited</p>
              <p>Session expires after 24 hours of inactivity</p>
            </div>
          </div>


        </div>

        {/* Footer */}
        <div className="text-center mt-6">
          <p className="text-gray-500 text-xs">
            Voice Clone Platform Admin Panel v1.0
          </p>
        </div>
      </div>
    </div>
  )
}
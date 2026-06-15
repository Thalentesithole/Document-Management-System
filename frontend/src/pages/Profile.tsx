import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { toast } from 'sonner'
import { Loader2, Save, User as UserIcon, Shield } from 'lucide-react'

export default function Profile() {
  const { user, updateProfile } = useAuth()
  const [fullName, setFullName] = useState(user?.full_name || '')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    if (password && password !== confirmPassword) {
      toast.error('Passwords do not match')
      return
    }
    if (password && password.length < 6) {
      toast.error('New password must be at least 6 characters')
      return
    }

    setLoading(true)
    try {
      await updateProfile(fullName, password || undefined)
      setPassword('')
      setConfirmPassword('')
      toast.success('Profile updated successfully!')
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Could not update profile'
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }

  const formatRole = (role?: string) => {
    if (!role) return '—'
    return role.replace('RoleEnum.', '').replace(/^\w/, (c) => c.toUpperCase())
  }

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Profile Settings
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Update your user name, credentials, and manage your account
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        {/* Profile Card */}
        <div className="md:col-span-1 rounded-xl border border-border bg-card p-6 flex flex-col items-center text-center justify-center space-y-4 shadow-sm">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 text-white shadow-lg">
            <UserIcon className="h-10 w-10" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-foreground">
              {user?.full_name || 'User'}
            </h2>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>

          <div className="inline-flex items-center gap-1.5 rounded-full bg-indigo-500/10 px-3 py-1 text-xs font-semibold text-indigo-400 border border-indigo-500/20">
            <Shield className="h-3.5 w-3.5" />
            {formatRole(user?.role)}
          </div>
        </div>

        {/* Edit Fields */}
        <div className="md:col-span-2 rounded-xl border border-border bg-card p-6 shadow-sm">
          <form onSubmit={handleSave} className="space-y-4">
            <div>
              <label className="mb-1.5 block text-xs font-medium text-muted-foreground">
                Email Address
              </label>
              <input
                type="text"
                value={user?.email || ''}
                disabled
                className="w-full rounded-xl border border-border bg-muted/50 px-4 py-2.5 text-sm text-muted-foreground cursor-not-allowed"
              />
            </div>

            <div>
              <label htmlFor="pname" className="mb-1.5 block text-xs font-medium text-foreground">
                Full Name
              </label>
              <input
                id="pname"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="John Doe"
                required
                className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground focus:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
              />
            </div>

            <div className="border-t border-border pt-4 mt-6">
              <h3 className="text-sm font-semibold text-foreground mb-4">
                Change Password
              </h3>
              <p className="text-xs text-muted-foreground mb-4">
                Leave these fields blank if you do not want to change your password
              </p>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label htmlFor="npass" className="mb-1.5 block text-xs font-medium text-foreground">
                    New Password
                  </label>
                  <input
                    id="npass"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground focus:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                  />
                </div>

                <div>
                  <label htmlFor="cpass" className="mb-1.5 block text-xs font-medium text-foreground">
                    Confirm Password
                  </label>
                  <input
                    id="cpass"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-sm text-foreground focus:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-4">
              <button
                type="submit"
                disabled={loading}
                className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:shadow-indigo-500/30 hover:brightness-110 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 disabled:opacity-60"
              >
                {loading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Save className="h-4 w-4" />
                )}
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

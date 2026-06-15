import { ShieldAlert } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function AccessDenied() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-4 text-center">
      <div className="mb-6 rounded-full bg-red-500/10 p-6">
        <ShieldAlert className="h-16 w-16 text-red-500" />
      </div>
      <h1 className="mb-2 text-3xl font-bold text-white">Access Denied</h1>
      <p className="mb-8 max-w-md text-slate-400">
        You don't have permission to access this page. If you believe this is an error, please contact your system administrator.
      </p>
      <Link
        to="/dashboard"
        className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white transition-colors hover:bg-indigo-500"
      >
        Return to Dashboard
      </Link>
    </div>
  )
}

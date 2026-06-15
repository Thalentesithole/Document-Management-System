import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import { format } from 'date-fns'
import { Shield, Loader2, Activity } from 'lucide-react'

interface AuditLog {
  id: string
  user_id: string | null
  user_email: string | null
  user_role: string | null
  action: string
  entity_type: string
  entity_id: string
  old_value: any
  new_value: any
  created_at: string
}

export default function AuditLogs() {
  const { data: logs, isLoading } = useQuery<AuditLog[]>({
    queryKey: ['audit-logs'],
    queryFn: async () => {
      const res = await api.get('/audit')
      return res.data
    },
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/10 text-indigo-400">
          <Shield className="h-5 w-5" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">System Audit Logs</h1>
          <p className="text-sm text-slate-400">Track and monitor all user actions securely</p>
        </div>
      </div>

      <div className="rounded-2xl border border-white/5 bg-white/5 backdrop-blur-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="border-b border-white/5 bg-black/20 text-xs font-semibold text-slate-400 uppercase">
              <tr>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">User</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Action</th>
                <th className="px-6 py-4">Entity</th>
                <th className="px-6 py-4">Entity ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    <Loader2 className="mx-auto mb-2 h-6 w-6 animate-spin text-indigo-400" />
                    Loading logs...
                  </td>
                </tr>
              ) : logs?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-slate-400">
                    <Activity className="mx-auto mb-2 h-6 w-6 text-slate-500" />
                    No audit logs recorded yet
                  </td>
                </tr>
              ) : (
                logs?.map((log) => (
                  <tr key={log.id} className="transition-colors hover:bg-white/5">
                    <td className="px-6 py-4 whitespace-nowrap text-xs">
                      {format(new Date(log.created_at), 'MMM d, yyyy HH:mm:ss')}
                    </td>
                    <td className="px-6 py-4 text-xs font-medium text-white">
                      {log.user_email || 'System'}
                    </td>
                    <td className="px-6 py-4">
                      {log.user_role && (
                        <span className="rounded bg-indigo-500/20 px-2 py-0.5 text-[10px] font-semibold text-indigo-300 uppercase tracking-wider border border-indigo-500/30">
                          {log.user_role}
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="rounded bg-slate-800 px-2 py-1 text-[10px] font-mono text-slate-300">
                        {log.action}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {log.entity_type}
                    </td>
                    <td className="px-6 py-4 font-mono text-[10px] text-slate-500">
                      {log.entity_id}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import {
  FileText, Clock, CheckCircle2, DollarSign, ArrowUpRight, Loader2, XCircle, Users, Receipt
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, AreaChart, Area
} from 'recharts'

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#3b82f6', '#10b981']

export default function Dashboard() {
  const { data: documents, isLoading: docsLoading } = useQuery({
    queryKey: ['documents-recent'],
    queryFn: async () => (await api.get('/documents/?limit=5')).data
  })

  const { data: spendData } = useQuery({
    queryKey: ['dash-spend-summary'],
    queryFn: async () => (await api.get('/reports/spend-summary')).data
  })

  const { data: vendorData } = useQuery({
    queryKey: ['dash-vendor-analysis'],
    queryFn: async () => (await api.get('/reports/vendor-analysis')).data
  })

  const { data: statusData } = useQuery({
    queryKey: ['dash-approval-status'],
    queryFn: async () => (await api.get('/reports/approval-status')).data
  })

  const { data: taxData } = useQuery({
    queryKey: ['dash-tax-vat'],
    queryFn: async () => (await api.get('/reports/tax-vat')).data
  })

  // Computed Stats
  const getStatusCount = (status: string) => {
    if (!statusData?.approval_status) return 0
    const item = statusData.approval_status.find((s: any) => s.status === status)
    return item ? item.count : 0
  }

  const totalDocuments = statusData?.approval_status?.reduce((acc: number, curr: any) => acc + curr.count, 0) || 0
  const pendingApprovals = getStatusCount('pending_review') + getStatusCount('pending_manager_approval') + getStatusCount('pending_final_approval')
  const approvedDocs = getStatusCount('approved')
  const rejectedDocs = getStatusCount('rejected')
  
  const totalSpend = spendData?.total_spend || 0
  const totalVat = taxData?.total_vat || 0
  const topVendorsCount = vendorData?.vendor_analysis?.length || 0

  const stats = [
    { label: 'Total Documents', value: totalDocuments, icon: FileText, gradient: 'from-blue-500 to-cyan-500', shadow: 'shadow-blue-500/20' },
    { label: 'Pending Approvals', value: pendingApprovals, icon: Clock, gradient: 'from-amber-500 to-orange-500', shadow: 'shadow-amber-500/20' },
    { label: 'Approved Docs', value: approvedDocs, icon: CheckCircle2, gradient: 'from-emerald-500 to-green-500', shadow: 'shadow-emerald-500/20' },
    { label: 'Rejected Docs', value: rejectedDocs, icon: XCircle, gradient: 'from-red-500 to-rose-500', shadow: 'shadow-red-500/20' },
    { label: 'Total Spend (Approved)', value: `$${totalSpend.toLocaleString(undefined, {minimumFractionDigits: 2})}`, icon: DollarSign, gradient: 'from-indigo-500 to-purple-500', shadow: 'shadow-indigo-500/20' },
    { label: 'Total VAT (Approved)', value: `$${totalVat.toLocaleString(undefined, {minimumFractionDigits: 2})}`, icon: Receipt, gradient: 'from-fuchsia-500 to-pink-500', shadow: 'shadow-fuchsia-500/20' },
    { label: 'Total Vendors', value: topVendorsCount, icon: Users, gradient: 'from-teal-500 to-emerald-500', shadow: 'shadow-teal-500/20' },
  ]

  const getStatusBadge = (status: string) => {
    const map: Record<string, string> = {
      pending_extraction: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
      pending_review: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
      pending_manager_approval: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      pending_final_approval: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      approved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      rejected: 'bg-red-500/10 text-red-400 border-red-500/20',
      returned_to_reviewer: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
      duplicate_flagged: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    }
    return map[status] || 'bg-slate-500/10 text-slate-400 border-slate-500/20'
  }

  const formatStatus = (status: string) => status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

  // Mock Trend Data for Area Chart (In a real app, this would come from a group_by month endpoint)
  const trendData = [
    { name: 'Jan', spend: totalSpend * 0.1 },
    { name: 'Feb', spend: totalSpend * 0.15 },
    { name: 'Mar', spend: totalSpend * 0.12 },
    { name: 'Apr', spend: totalSpend * 0.2 },
    { name: 'May', spend: totalSpend * 0.18 },
    { name: 'Jun', spend: totalSpend * 0.25 },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="mt-1 text-sm text-muted-foreground">Overview of your document processing pipeline</p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4">
        {stats.map((stat) => (
          <div key={stat.label} className="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-all duration-300 hover:shadow-lg hover:-translate-y-0.5">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{stat.label}</p>
                <p className="mt-2 text-2xl font-bold text-foreground">{stat.value}</p>
              </div>
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${stat.gradient} shadow-lg ${stat.shadow}`}>
                <stat.icon className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className={`absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r ${stat.gradient} opacity-0 transition-opacity duration-300 group-hover:opacity-100`} />
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Vendor Spend Analysis */}
        <div className="lg:col-span-2 rounded-xl border border-border bg-card p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-foreground mb-6">Vendor Spend Analysis</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={spendData?.spend_by_vendor?.slice(0, 7) || []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                <XAxis dataKey="vendor" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip cursor={{fill: '#334155', opacity: 0.2}} contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff'}} />
                <Bar dataKey="total_spend" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Approval Status Breakdown */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-foreground mb-6">Approval Status Breakdown</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={statusData?.approval_status || []} dataKey="count" nameKey="status" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5}>
                  {statusData?.approval_status?.map((entry: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff'}} formatter={(value: number, name: string) => [value, formatStatus(name)]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-2 justify-center mt-2">
            {statusData?.approval_status?.map((s: any, i: number) => (
              <div key={i} className="flex items-center gap-1.5 text-xs">
                <span className="w-2.5 h-2.5 rounded-full" style={{backgroundColor: COLORS[i % COLORS.length]}}></span>
                <span className="text-muted-foreground">{formatStatus(s.status)}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Spend Trend and Recent Docs Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Monthly Spend Trend */}
        <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-foreground mb-6">Estimated Spend Trend</h2>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorSpend" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                <XAxis dataKey="name" stroke="#888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px', color: '#fff'}} />
                <Area type="monotone" dataKey="spend" stroke="#10b981" fillOpacity={1} fill="url(#colorSpend)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent documents */}
        <div className="rounded-xl border border-border bg-card shadow-sm flex flex-col">
          <div className="flex items-center justify-between border-b border-border px-6 py-4">
            <h2 className="text-sm font-semibold text-foreground">Recent Documents</h2>
            <a href="/documents" className="flex items-center gap-1 text-xs font-medium text-indigo-500 hover:text-indigo-400 transition-colors">
              View all <ArrowUpRight className="h-3.5 w-3.5" />
            </a>
          </div>
          <div className="flex-1 overflow-y-auto">
            {docsLoading ? (
              <div className="flex items-center justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-muted-foreground" /></div>
            ) : documents && documents.length > 0 ? (
              <div className="divide-y divide-border">
                {documents.map((doc: any) => (
                  <div key={doc.id} className="flex items-center justify-between px-6 py-4 hover:bg-muted/50 transition-colors">
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-400">
                        <FileText className="h-5 w-5" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-foreground truncate">{doc.file_name}</p>
                        <p className="text-xs text-muted-foreground">{doc.vendor_name || 'Processing…'}</p>
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1.5">
                      {doc.total_amount && (
                        <span className="text-sm font-bold text-foreground">
                          {doc.currency || '$'}{Number(doc.total_amount).toLocaleString()}
                        </span>
                      )}
                      <span className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ${getStatusBadge(doc.status)}`}>
                        {formatStatus(doc.status)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-12 text-center h-full">
                <FileText className="h-10 w-10 text-muted-foreground/40 mb-3" />
                <p className="text-sm text-muted-foreground">No documents yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

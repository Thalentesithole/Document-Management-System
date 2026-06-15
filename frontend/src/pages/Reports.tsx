import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts'
import { FileSpreadsheet, FileText, Loader2, Search } from 'lucide-react'
import * as XLSX from 'xlsx'
import jsPDF from 'jspdf'
import autoTable from 'jspdf-autotable'

const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#14b8a6', '#f59e0b', '#3b82f6', '#10b981']

export default function Reports() {
  const [activeTab, setActiveTab] = useState<'spend' | 'vendor' | 'status' | 'tax'>('spend')
  
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    vendorName: '',
    status: ''
  })

  // Queries
  const { data: spendData, isLoading: isLoadingSpend } = useQuery({
    queryKey: ['report-spend', filters],
    queryFn: async () => (await api.get('/reports/spend-summary', { params: filters })).data
  })

  const { data: vendorData, isLoading: isLoadingVendor } = useQuery({
    queryKey: ['report-vendor', filters],
    queryFn: async () => (await api.get('/reports/vendor-analysis', { params: filters })).data
  })

  const { data: statusData, isLoading: isLoadingStatus } = useQuery({
    queryKey: ['report-status', filters],
    queryFn: async () => (await api.get('/reports/approval-status', { params: filters })).data
  })

  const { data: taxData, isLoading: isLoadingTax } = useQuery({
    queryKey: ['report-tax', filters],
    queryFn: async () => (await api.get('/reports/tax-vat', { params: filters })).data
  })

  // Export handlers
  const exportExcel = (data: any[], filename: string) => {
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, "Report")
    XLSX.writeFile(wb, `${filename}.xlsx`)
  }

  const exportPDF = (title: string, columns: string[], data: any[][]) => {
    const doc = new jsPDF()
    doc.text(title, 14, 15)
    doc.setFontSize(10)
    doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 14, 22)
    
    autoTable(doc, {
      startY: 30,
      head: [columns],
      body: data,
    })
    
    doc.save(`${title.toLowerCase().replace(/\s+/g, '_')}.pdf`)
  }

  // Handle specific exports
  const handleExport = (format: 'pdf' | 'excel') => {
    if (activeTab === 'spend' && spendData) {
      if (format === 'excel') exportExcel(spendData.spend_by_vendor, 'Spend_Summary')
      else exportPDF('Spend Summary Report', ['Vendor', 'Total Spend'], spendData.spend_by_vendor.map((r: any) => [r.vendor, `$${r.total_spend.toFixed(2)}`]))
    }
    if (activeTab === 'vendor' && vendorData) {
      if (format === 'excel') exportExcel(vendorData.vendor_analysis, 'Vendor_Analysis')
      else exportPDF('Vendor Analysis Report', ['Vendor', 'Total Spend', 'Doc Count', 'Avg Invoice Value'], vendorData.vendor_analysis.map((r: any) => [r.vendor_name, `$${r.total_spend.toFixed(2)}`, r.document_count, `$${r.average_invoice_value.toFixed(2)}`]))
    }
    if (activeTab === 'status' && statusData) {
      if (format === 'excel') exportExcel(statusData.approval_status, 'Approval_Status')
      else exportPDF('Approval Status Report', ['Status', 'Count'], statusData.approval_status.map((r: any) => [r.status.replace(/_/g, ' '), r.count]))
    }
    if (activeTab === 'tax' && taxData) {
      if (format === 'excel') exportExcel(taxData.vat_by_vendor, 'Tax_VAT_Report')
      else exportPDF('Tax VAT Report', ['Vendor', 'Total VAT'], taxData.vat_by_vendor.map((r: any) => [r.vendor_name, `$${r.total_vat.toFixed(2)}`]))
    }
  }

  const tabs = [
    { id: 'spend', label: 'Spend Summary' },
    { id: 'vendor', label: 'Vendor Analysis' },
    { id: 'status', label: 'Approval Status' },
    { id: 'tax', label: 'Tax / VAT' },
  ]

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Reports Center</h1>
          <p className="text-sm text-muted-foreground mt-1">Analytics, trends, and data exports</p>
        </div>
        
        <div className="flex items-center gap-3">
          <button onClick={() => handleExport('excel')} className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors">
            <FileSpreadsheet className="h-4 w-4 text-emerald-500" />
            Export Excel
          </button>
          <button onClick={() => handleExport('pdf')} className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium text-foreground hover:bg-muted transition-colors">
            <FileText className="h-4 w-4 text-red-500" />
            Export PDF
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 rounded-xl border border-border bg-card p-4">
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase mb-1.5 block">Start Date</label>
          <input type="date" value={filters.startDate} onChange={e => setFilters({...filters, startDate: e.target.value})} className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-indigo-500 outline-none" />
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase mb-1.5 block">End Date</label>
          <input type="date" value={filters.endDate} onChange={e => setFilters({...filters, endDate: e.target.value})} className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-indigo-500 outline-none" />
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase mb-1.5 block">Vendor</label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input type="text" placeholder="Search vendor..." value={filters.vendorName} onChange={e => setFilters({...filters, vendorName: e.target.value})} className="w-full rounded-lg border border-border bg-background pl-9 pr-3 py-2 text-sm focus:border-indigo-500 outline-none" />
          </div>
        </div>
        <div>
          <label className="text-xs font-semibold text-muted-foreground uppercase mb-1.5 block">Status</label>
          <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})} className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm focus:border-indigo-500 outline-none">
            <option value="">All Statuses</option>
            <option value="pending_review">Pending Review</option>
            <option value="pending_manager_approval">Pending Manager Approval</option>
            <option value="pending_final_approval">Pending Final Approval</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="returned_to_reviewer">Returned to Reviewer</option>
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 rounded-lg bg-muted/50 p-1 overflow-x-auto">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex-1 rounded-md px-3 py-2 text-sm font-medium transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:bg-background/50 hover:text-foreground'}`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        
        {/* Spend Summary Tab */}
        {activeTab === 'spend' && (
          <div className="p-6">
            {isLoadingSpend ? <div className="flex py-10 justify-center"><Loader2 className="animate-spin text-muted-foreground" /></div> : (
              <div className="space-y-8">
                <div className="rounded-xl border border-indigo-500/20 bg-indigo-500/5 p-6 text-center">
                  <p className="text-sm font-medium text-indigo-400">Total Spend</p>
                  <h3 className="text-4xl font-bold text-foreground mt-2">${spendData?.total_spend?.toLocaleString(undefined, {minimumFractionDigits: 2}) || '0.00'}</h3>
                </div>
                
                <div className="h-[400px]">
                  <h3 className="text-sm font-semibold mb-4 text-muted-foreground uppercase">Spend Distribution by Vendor</h3>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={spendData?.spend_by_vendor || []}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                      <XAxis dataKey="vendor" stroke="#888" />
                      <YAxis stroke="#888" />
                      <RechartsTooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                      <Bar dataKey="total_spend" fill="#6366f1" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Vendor Analysis Tab */}
        {activeTab === 'vendor' && (
          <div className="p-6">
            {isLoadingVendor ? <div className="flex py-10 justify-center"><Loader2 className="animate-spin text-muted-foreground" /></div> : (
              <div className="space-y-6">
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/30 text-muted-foreground">
                        <th className="px-4 py-3 font-semibold uppercase">Vendor Name</th>
                        <th className="px-4 py-3 font-semibold uppercase text-right">Documents</th>
                        <th className="px-4 py-3 font-semibold uppercase text-right">Avg Value</th>
                        <th className="px-4 py-3 font-semibold uppercase text-right">Total Spend</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {vendorData?.vendor_analysis?.map((v: any, i: number) => (
                        <tr key={i} className="hover:bg-muted/10">
                          <td className="px-4 py-3 font-medium">{v.vendor_name}</td>
                          <td className="px-4 py-3 text-right">{v.document_count}</td>
                          <td className="px-4 py-3 text-right">${v.average_invoice_value?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                          <td className="px-4 py-3 text-right font-semibold text-indigo-400">${v.total_spend?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Approval Status Tab */}
        {activeTab === 'status' && (
          <div className="p-6">
            {isLoadingStatus ? <div className="flex py-10 justify-center"><Loader2 className="animate-spin text-muted-foreground" /></div> : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
                <div className="h-[400px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={statusData?.approval_status || []} dataKey="count" nameKey="status" cx="50%" cy="50%" innerRadius={80} outerRadius={120} paddingAngle={5}>
                        {statusData?.approval_status?.map((_: any, index: number) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="space-y-4">
                  {statusData?.approval_status?.map((s: any, i: number) => (
                    <div key={i} className="flex items-center justify-between p-4 rounded-xl border border-border bg-background">
                      <div className="flex items-center gap-3">
                        <div className="w-3 h-3 rounded-full" style={{backgroundColor: COLORS[i % COLORS.length]}}></div>
                        <span className="font-medium capitalize">{s.status.replace(/_/g, ' ')}</span>
                      </div>
                      <span className="text-xl font-bold">{s.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tax VAT Tab */}
        {activeTab === 'tax' && (
          <div className="p-6">
            {isLoadingTax ? <div className="flex py-10 justify-center"><Loader2 className="animate-spin text-muted-foreground" /></div> : (
              <div className="space-y-8">
                <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-6 text-center">
                  <p className="text-sm font-medium text-emerald-400">Total VAT Collected / Paid</p>
                  <h3 className="text-4xl font-bold text-foreground mt-2">${taxData?.total_vat?.toLocaleString(undefined, {minimumFractionDigits: 2}) || '0.00'}</h3>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/30 text-muted-foreground">
                        <th className="px-4 py-3 font-semibold uppercase">Vendor Name</th>
                        <th className="px-4 py-3 font-semibold uppercase text-right">VAT Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                      {taxData?.vat_by_vendor?.map((v: any, i: number) => (
                        <tr key={i} className="hover:bg-muted/10">
                          <td className="px-4 py-3 font-medium">{v.vendor_name}</td>
                          <td className="px-4 py-3 text-right font-semibold text-emerald-400">${v.total_vat?.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  )
}

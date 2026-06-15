import { useQuery } from '@tanstack/react-query'
import api from '@/services/api'
import {
  FileText,
  Loader2,
  Search,
  X,
  AlertCircle,
  Eye,
  History,
  RotateCcw,
} from 'lucide-react'
import { useState } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { toast } from 'sonner'

interface Document {
  id: string
  file_name: string
  file_url: string
  vendor_name: string | null
  invoice_number: string | null
  invoice_date: string | null
  total_amount: number | null
  currency: string | null
  subtotal_amount: number | null
  vat_amount: number | null
  confidence_score: number | null
  document_type: string | null
  status: string
  uploaded_by: string
  created_at: string
}

interface WorkflowHistoryItem {
  id: string
  stage_number: number
  action: string
  comments: string
  approved_at: string
  approver_name: string
  approver_role: string
}

const statusStyles: Record<string, string> = {
  pending_extraction: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  pending_review: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  pending_manager_approval: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  pending_final_approval: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  approved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  rejected: 'bg-red-500/10 text-red-400 border-red-500/20',
  returned_to_reviewer: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  duplicate_flagged: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
}

const formatStatus = (status: string) =>
  status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

export default function Documents() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null)
  const [actionComments, setActionComments] = useState('')
  const [submittingAction, setSubmittingAction] = useState(false)

  const { data: documents, isLoading, refetch } = useQuery<Document[]>({
    queryKey: ['documents'],
    queryFn: async () => {
      const res = await api.get('/documents/')
      return res.data
    },
  })

  const { data: docDetail, isLoading: isDetailLoading } = useQuery<Document>({
    queryKey: ['document-detail', selectedDocId],
    queryFn: async () => {
      const res = await api.get(`/documents/${selectedDocId}`)
      return res.data
    },
    enabled: !!selectedDocId,
  })

  const { data: workflowHistory } = useQuery<WorkflowHistoryItem[]>({
    queryKey: ['document-history', selectedDocId],
    queryFn: async () => {
      const res = await api.get(`/workflow/${selectedDocId}/history`)
      return res.data
    },
    enabled: !!selectedDocId,
  })

  const filtered = documents?.filter(
    (doc) =>
      doc.file_name.toLowerCase().includes(search.toLowerCase()) ||
      doc.vendor_name?.toLowerCase().includes(search.toLowerCase()) ||
      doc.invoice_number?.toLowerCase().includes(search.toLowerCase())
  )

  const getRoleClean = (roleString?: string) => {
    if (!roleString) return ''
    return roleString.replace('RoleEnum.', '').toLowerCase()
  }

  // ==========================================
  // 3-Stage Workflow Authorization Logic
  // ==========================================
  const getWorkflowAuthorization = (doc: Document) => {
    if (!user) return { allowed: false, reason: 'Not logged in' }

    // Rule: Cannot approve your own upload
    if (doc.uploaded_by === user.id) {
      return { allowed: false, reason: 'You cannot approve a document you uploaded yourself.' }
    }

    const cleanRole = getRoleClean(user.role)

    // Stage 1: Reviewer — pending_review, duplicate_flagged, returned_to_reviewer
    if (doc.status === 'pending_review' || doc.status === 'duplicate_flagged' || doc.status === 'returned_to_reviewer') {
      if (cleanRole === 'reviewer' || cleanRole === 'admin') {
        return { allowed: true, stage: 1, canReturn: false }
      }
      return { allowed: false, reason: 'Only users with the Reviewer or Admin role can perform Stage 1 review.' }
    }

    // Stage 2: Manager — pending_manager_approval
    if (doc.status === 'pending_manager_approval') {
      if (cleanRole === 'manager' || cleanRole === 'admin') {
        return { allowed: true, stage: 2, canReturn: true }
      }
      return { allowed: false, reason: 'Only users with the Manager or Admin role can perform Stage 2 approval.' }
    }

    // Stage 3: Finance / Admin — pending_final_approval
    if (doc.status === 'pending_final_approval') {
      if (cleanRole === 'admin') {
        return { allowed: true, stage: 3, canReturn: false }
      }
      return { allowed: false, reason: 'Only Admins can perform final Stage 3 approval.' }
    }
    return { allowed: false, reason: 'This document is not currently in an active approval stage.' }
  }

  const handleWorkflowAction = async (action: 'approve' | 'reject' | 'return') => {
    if (!selectedDocId) return
    setSubmittingAction(true)
    try {
      await api.post(`/workflow/${selectedDocId}/${action}`, {
        comments: actionComments,
      })
      const messages: Record<string, string> = {
        approve: 'Document approved successfully!',
        reject: 'Document rejected successfully!',
        return: 'Document returned to reviewer successfully!',
      }
      toast.success(messages[action])
      setActionComments('')
      refetch()
      setSelectedDocId(null)
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Failed to submit action'
      toast.error(message)
    } finally {
      setSubmittingAction(false)
    }
  }

  const handleViewDocument = async () => {
    if (!docDetail) return
    try {
      const res = await api.get(`/documents/${docDetail.id}/download`, { responseType: 'blob' })
      const fileURL = URL.createObjectURL(res.data)
      window.open(fileURL, '_blank')
    } catch (err) {
      toast.error('Failed to open document. It may have been removed or you lack permission.')
    }
  }



  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Documents
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            All uploaded invoices and their extraction results
          </p>
        </div>

        {/* Search */}
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents…"
            className="w-full rounded-xl border border-border bg-background py-2.5 pl-10 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:border-indigo-500/50 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 transition-all"
          />
        </div>
      </div>

      {/* Table */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : filtered && filtered.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-muted/30">
                  <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Vendor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Invoice #
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filtered.map((doc) => (
                  <tr
                    key={doc.id}
                    className="hover:bg-muted/20 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted">
                          <FileText className="h-4 w-4 text-muted-foreground" />
                        </div>
                        <span className="text-sm font-medium text-foreground truncate max-w-[200px]">
                          {doc.file_name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {doc.vendor_name || '—'}
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground font-mono">
                      {doc.invoice_number || '—'}
                    </td>
                    <td className="px-6 py-4 text-right text-sm font-medium text-foreground">
                      {doc.total_amount
                        ? `${doc.currency || '$'}${Number(doc.total_amount).toLocaleString()}`
                        : '—'}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${
                          statusStyles[doc.status] ||
                          'bg-slate-500/10 text-slate-400 border-slate-500/20'
                        }`}
                      >
                        {formatStatus(doc.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedDocId(doc.id)}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-background px-3 py-1.5 text-xs font-semibold text-foreground hover:bg-muted transition-all"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        Review / History
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <FileText className="h-10 w-10 text-muted-foreground/40 mb-3" />
            <p className="text-sm text-muted-foreground">
              {search
                ? 'No documents match your search.'
                : 'No documents found. Upload your first invoice.'}
            </p>
          </div>
        )}
      </div>

      {/* Review & Workflow Modal */}
      {selectedDocId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
          <div className="relative w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-2xl border border-white/10 bg-slate-900 text-white shadow-2xl p-6 md:p-8 space-y-6">
            
            {/* Modal Header */}
            <div className="flex items-start justify-between border-b border-white/10 pb-4">
              <div>
                <h2 className="text-xl font-bold truncate max-w-[500px]">
                  {docDetail?.file_name || 'Loading details…'}
                </h2>
                <div className="mt-1.5 flex flex-wrap items-center gap-2">
                  {docDetail && (
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-[11px] font-medium ${statusStyles[docDetail.status]}`}>
                      {formatStatus(docDetail.status)}
                    </span>
                  )}
                  <span className="text-xs text-slate-400">
                    ID: {selectedDocId}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedDocId(null)}
                className="h-8 w-8 flex items-center justify-center rounded-lg border border-white/10 text-slate-400 hover:text-white hover:bg-white/5 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {isDetailLoading ? (
              <div className="flex items-center justify-center py-16">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-500" />
              </div>
            ) : docDetail ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Extraction Fields Panel */}
                <div className="md:col-span-2 space-y-6">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">
                      Extracted Information
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 rounded-xl border border-white/5 bg-white/5 p-4">
                      <div>
                        <p className="text-[11px] text-slate-500">Vendor Name</p>
                        <p className="text-sm font-medium">{docDetail.vendor_name || '—'}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Invoice Number</p>
                        <p className="text-sm font-medium font-mono">{docDetail.invoice_number || '—'}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Invoice Date</p>
                        <p className="text-sm font-medium">
                          {docDetail.invoice_date
                            ? new Date(docDetail.invoice_date).toLocaleDateString('en-US', {
                                month: 'short',
                                day: 'numeric',
                                year: 'numeric',
                              })
                            : '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Currency</p>
                        <p className="text-sm font-medium">{docDetail.currency || '—'}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Document Type</p>
                        <p className="text-sm font-medium capitalize">{docDetail.document_type ? docDetail.document_type.replace('_', ' ') : '—'}</p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Confidence Score</p>
                        <p className="text-sm font-medium">
                          {docDetail.confidence_score ? `${(Number(docDetail.confidence_score) * 100).toFixed(1)}%` : '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">Subtotal Amount</p>
                        <p className="text-sm font-medium">
                          {docDetail.subtotal_amount
                            ? `${docDetail.currency || ''} ${Number(docDetail.subtotal_amount).toLocaleString()}`
                            : '—'}
                        </p>
                      </div>
                      <div>
                        <p className="text-[11px] text-slate-500">VAT Amount</p>
                        <p className="text-sm font-medium">
                          {docDetail.vat_amount
                            ? `${docDetail.currency || ''} ${Number(docDetail.vat_amount).toLocaleString()}`
                            : '—'}
                        </p>
                      </div>
                      <div className="sm:col-span-2 border-t border-white/5 pt-3 mt-1">
                        <p className="text-[11px] text-slate-500">Total Amount</p>
                        <p className="text-lg font-bold text-indigo-400">
                          {docDetail.total_amount
                            ? `${docDetail.currency || ''} ${Number(docDetail.total_amount).toLocaleString()}`
                            : '—'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Document URL Preview */}
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Original File
                    </h3>
                    <button
                      onClick={handleViewDocument}
                      className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-4 py-2.5 text-sm font-semibold hover:bg-white/5 transition-colors"
                    >
                      <FileText className="h-4 w-4 text-indigo-400" />
                      View Uploaded Document Link
                    </button>
                  </div>
                </div>

                {/* Workflow / Approvals Sidebar */}
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">
                      Approval Tracking
                    </h3>

                    {/* 3-Step Visualizer */}
                    <div className="space-y-3">
                      {/* Stage 1: Reviewer */}
                      <div className="flex items-center gap-2.5">
                        <div className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                          docDetail.status === 'pending_review' || docDetail.status === 'duplicate_flagged' || docDetail.status === 'returned_to_reviewer'
                            ? 'bg-amber-500 text-slate-950 ring-4 ring-amber-500/20'
                            : ['pending_manager_approval', 'pending_final_approval', 'approved'].includes(docDetail.status)
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-white/10 text-slate-400'
                        }`}>
                          1
                        </div>
                        <div className="flex-1 text-xs">
                          <p className="font-semibold">Stage 1: Reviewer</p>
                          <p className="text-[10px] text-slate-400">Verify extracted data & duplicates</p>
                        </div>
                      </div>

                      {/* Stage 2: Manager */}
                      <div className="flex items-center gap-2.5">
                        <div className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                          docDetail.status === 'pending_manager_approval'
                            ? 'bg-orange-500 text-slate-950 ring-4 ring-orange-500/20'
                            : ['pending_final_approval', 'approved'].includes(docDetail.status)
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-white/10 text-slate-400'
                        }`}>
                          2
                        </div>
                        <div className="flex-1 text-xs">
                          <p className="font-semibold">Stage 2: Manager</p>
                          <p className="text-[10px] text-slate-400">Operational & business review</p>
                        </div>
                      </div>

                      {/* Stage 3: Finance / Admin */}
                      <div className="flex items-center gap-2.5">
                        <div className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                          docDetail.status === 'pending_final_approval'
                            ? 'bg-purple-500 text-slate-950 ring-4 ring-purple-500/20'
                            : docDetail.status === 'approved'
                            ? 'bg-emerald-500 text-slate-950'
                            : 'bg-white/10 text-slate-400'
                        }`}>
                          3
                        </div>
                        <div className="flex-1 text-xs">
                          <p className="font-semibold">Stage 3: Admin</p>
                          <p className="text-[10px] text-slate-400">Final financial sign-off</p>
                        </div>
                      </div>

                    </div>
                  </div>

                  {/* History Logs */}
                  {workflowHistory && workflowHistory.length > 0 && (
                    <div className="border-t border-white/10 pt-4">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 uppercase tracking-wider mb-3">
                        <History className="h-4 w-4" />
                        Audit History
                      </div>
                      <div className="space-y-3 max-h-[150px] overflow-y-auto text-xs pr-1">
                        {workflowHistory.map((item) => (
                          <div key={item.id} className="rounded-lg bg-white/5 p-2.5 border border-white/5 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className={`font-semibold capitalize ${
                                item.action === 'approve' ? 'text-emerald-400'
                                : item.action === 'return' ? 'text-yellow-400'
                                : 'text-red-400'
                              }`}>
                                {item.action === 'approve' ? 'Approved'
                                  : item.action === 'return' ? 'Returned'
                                  : 'Rejected'} (Stg {item.stage_number})
                              </span>
                              <span className="text-[9px] text-slate-500">
                                {new Date(item.approved_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-[10px] text-slate-300 font-medium">By: {item.approver_name}</p>
                            {item.comments && (
                              <p className="text-[10px] italic text-slate-400 bg-black/20 p-1.5 rounded mt-1">
                                "{item.comments}"
                              </p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Decision Panel */}
                  <div className="border-t border-white/10 pt-4 space-y-3">
                    <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                      Workflow Action
                    </h4>

                    {(() => {
                      const auth = getWorkflowAuthorization(docDetail)
                      if (!auth.allowed) {
                        return (
                          <div className="flex items-start gap-2 rounded-xl bg-white/5 border border-white/5 p-3 text-xs text-slate-400">
                            <AlertCircle className="h-4 w-4 shrink-0 text-slate-500" />
                            <p>{auth.reason}</p>
                          </div>
                        )
                      }

                      const stageNames: Record<number, string> = {
                        1: 'Reviewer',
                        2: 'Manager',
                        3: 'Finance / Admin',
                      }

                      return (
                        <div className="space-y-3">
                          <p className="text-xs text-indigo-300 font-medium">
                            You are authorized to review this document as a Stage {auth.stage} ({stageNames[auth.stage!]}) approver.
                          </p>
                          <div>
                            <label htmlFor="comments" className="mb-1 block text-[10px] text-slate-400 uppercase font-semibold">
                              Comments / Reasons
                            </label>
                            <textarea
                              id="comments"
                              value={actionComments}
                              onChange={(e) => setActionComments(e.target.value)}
                              placeholder="e.g. Budget matches Q2 projections..."
                              rows={3}
                              className="w-full rounded-lg border border-white/10 bg-white/5 p-2 text-xs text-white focus:border-indigo-500/50 focus:outline-none focus:ring-1 focus:ring-indigo-500/20"
                            />
                          </div>

                          <div className={`grid gap-2 ${auth.canReturn ? 'grid-cols-3' : 'grid-cols-2'}`}>
                            <button
                              onClick={() => handleWorkflowAction('reject')}
                              disabled={submittingAction}
                              className="flex items-center justify-center gap-1.5 rounded-lg border border-red-500/30 bg-red-500/10 py-2 text-xs font-semibold text-red-400 hover:bg-red-500/20 disabled:opacity-50"
                            >
                              Reject
                            </button>
                            {auth.canReturn && (
                              <button
                                onClick={() => handleWorkflowAction('return')}
                                disabled={submittingAction}
                                className="flex items-center justify-center gap-1.5 rounded-lg border border-yellow-500/30 bg-yellow-500/10 py-2 text-xs font-semibold text-yellow-400 hover:bg-yellow-500/20 disabled:opacity-50"
                              >
                                <RotateCcw className="h-3 w-3" />
                                Return
                              </button>
                            )}
                            <button
                              onClick={() => handleWorkflowAction('approve')}
                              disabled={submittingAction}
                              className="flex items-center justify-center gap-1.5 rounded-lg bg-emerald-600 py-2 text-xs font-semibold text-white hover:bg-emerald-500 disabled:opacity-50"
                            >
                              Approve
                            </button>
                          </div>
                        </div>
                      )
                    })()}
                  </div>

                </div>

              </div>
            ) : null}

          </div>
        </div>
      )}
    </div>
  )
}

import { useState, useCallback } from 'react'
import { useMutation } from '@tanstack/react-query'
import api from '@/services/api'
import { toast } from 'sonner'
import {
  Upload as UploadIcon,
  FileUp,
  X,
  CheckCircle2,
  Loader2,
  FileText,
} from 'lucide-react'

const ACCEPTED_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
]
const MAX_SIZE = 20 * 1024 * 1024 // 20MB

export default function Upload() {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const uploadMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      const res = await api.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return res.data
    },
    onSuccess: (data) => {
      toast.success('Document uploaded successfully! Extraction has started.', {
        description: `Document ID: ${data.document_id}`,
      })
      setSelectedFile(null)
    },
    onError: (err: unknown) => {
      const message =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail || 'Upload failed. Please try again.'
      toast.error(message)
    },
  })

  const handleFile = useCallback((file: File) => {
    if (!ACCEPTED_TYPES.includes(file.type)) {
      toast.error('Unsupported file format. Please use PDF, PNG, or JPG.')
      return
    }
    if (file.size > MAX_SIZE) {
      toast.error('File too large. Maximum size is 20MB.')
      return
    }
    setSelectedFile(file)
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragActive(false)
      const file = e.dataTransfer.files?.[0]
      if (file) handleFile(file)
    },
    [handleFile]
  )

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragActive(false)
  }, [])

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Upload Document
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Upload invoices or receipts for AI-powered data extraction
        </p>
      </div>

      {/* Upload zone */}
      <div className="mx-auto max-w-2xl">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          className={`
            relative flex flex-col items-center justify-center rounded-2xl border-2 border-dashed p-12
            transition-all duration-300 cursor-pointer
            ${
              dragActive
                ? 'border-indigo-500 bg-indigo-500/5 scale-[1.02]'
                : 'border-border hover:border-indigo-500/50 hover:bg-muted/50'
            }
          `}
          onClick={() => document.getElementById('file-input')?.click()}
        >
          <input
            id="file-input"
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleInputChange}
            className="hidden"
          />

          <div
            className={`mb-4 flex h-16 w-16 items-center justify-center rounded-2xl transition-all duration-300 ${
              dragActive
                ? 'bg-indigo-500/20 shadow-lg shadow-indigo-500/20'
                : 'bg-muted'
            }`}
          >
            <UploadIcon
              className={`h-8 w-8 transition-colors ${
                dragActive ? 'text-indigo-400' : 'text-muted-foreground'
              }`}
            />
          </div>

          <p className="text-sm font-medium text-foreground">
            {dragActive ? 'Drop your file here' : 'Drag & drop your document'}
          </p>
          <p className="mt-1.5 text-xs text-muted-foreground">
            or click to browse • PDF, PNG, JPG up to 20MB
          </p>
        </div>

        {/* Selected file preview */}
        {selectedFile && (
          <div className="mt-6 rounded-xl border border-border bg-card p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 min-w-0">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500/10 to-purple-500/10 border border-indigo-500/20">
                  <FileText className="h-5 w-5 text-indigo-400" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {selectedFile.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatFileSize(selectedFile.size)} •{' '}
                    {selectedFile.type.split('/')[1].toUpperCase()}
                  </p>
                </div>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedFile(null)
                }}
                className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <button
              onClick={() => uploadMutation.mutate(selectedFile)}
              disabled={uploadMutation.isPending}
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:shadow-indigo-500/30 hover:brightness-110 disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {uploadMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Uploading & extracting…
                </>
              ) : uploadMutation.isSuccess ? (
                <>
                  <CheckCircle2 className="h-4 w-4" />
                  Uploaded successfully
                </>
              ) : (
                <>
                  <FileUp className="h-4 w-4" />
                  Upload & extract data
                </>
              )}
            </button>
          </div>
        )}

        {/* Info cards */}
        <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
          {[
            {
              title: 'AI Extraction',
              desc: 'Vendor, amounts, dates — extracted automatically',
            },
            {
              title: 'Duplicate Detection',
              desc: 'Duplicates are flagged before approval',
            },
            {
              title: 'Approval Workflow',
              desc: 'Multi-step review and approval pipeline',
            },
          ].map((card) => (
            <div
              key={card.title}
              className="rounded-xl border border-border bg-card p-4"
            >
              <p className="text-sm font-medium text-foreground">
                {card.title}
              </p>
              <p className="mt-1 text-xs text-muted-foreground">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

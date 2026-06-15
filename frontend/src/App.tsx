import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'sonner'
import { AppShell } from '@/layouts/AppShell'

// Pages
import Dashboard from '@/pages/Dashboard'
import Login from '@/pages/Login'
import Upload from '@/pages/Upload'
import Documents from '@/pages/Documents'
import ForgotPassword from '@/pages/ForgotPassword'
import ResetPassword from '@/pages/ResetPassword'
import Profile from '@/pages/Profile'
import AccessDenied from '@/pages/AccessDenied'
import AuditLogs from '@/pages/AuditLogs'

import Reports from '@/pages/Reports'

// Auth Context
import { AuthProvider, useAuth } from '@/contexts/AuthContext'

const queryClient = new QueryClient()

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex h-screen items-center justify-center text-white bg-slate-950">Loading...</div>
  if (!user) return <Navigate to="/login" />
  return <>{children}</>
}

function RoleProtectedRoute({ children, allowedRoles }: { children: React.ReactNode, allowedRoles: string[] }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex h-screen items-center justify-center text-white bg-slate-950">Loading...</div>
  if (!user) return <Navigate to="/login" />
  if (!allowedRoles.includes(user.role)) return <Navigate to="/access-denied" />
  return <>{children}</>
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            
            <Route path="/" element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="upload" element={<RoleProtectedRoute allowedRoles={['admin', 'reviewer']}><Upload /></RoleProtectedRoute>} />
              <Route path="documents" element={<Documents />} />
              <Route path="reports" element={<RoleProtectedRoute allowedRoles={['admin', 'manager']}><Reports /></RoleProtectedRoute>} />
              <Route path="profile" element={<Profile />} />
              <Route path="audit-logs" element={<RoleProtectedRoute allowedRoles={['admin']}><AuditLogs /></RoleProtectedRoute>} />
            </Route>
            <Route path="/access-denied" element={<AccessDenied />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  )
}


export default App

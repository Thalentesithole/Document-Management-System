import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import {
  LayoutDashboard,
  Upload,
  FileText,
  LogOut,
  Menu,
  X,
  ChevronLeft,
  User as UserIcon,
  BarChart3
  Shield
} from 'lucide-react'

export function AppShell() {
  const { user, logout, isAdmin, isManager, isReviewer } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, show: true },
    { to: '/upload', label: 'Upload', icon: Upload, show: isAdmin || isReviewer },
    { to: '/documents', label: 'Documents', icon: FileText, show: true },
    { to: '/reports', label: 'Reports', icon: BarChart3, show: isAdmin || isManager },
    { to: '/profile', label: 'Profile', icon: UserIcon, show: true },
    { to: '/audit-logs', label: 'Audit Logs', icon: Shield, show: isAdmin },
  ].filter(item => item.show)


  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      {/* Mobile overlay */}
      {mobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-50 flex flex-col
          border-r border-white/10
          bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950
          backdrop-blur-xl shadow-2xl
          transition-all duration-300 ease-in-out
          lg:relative
          ${collapsed ? 'w-[72px]' : 'w-64'}
          ${mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
        `}
      >
        {/* Logo area */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-white/5">
          {!collapsed && (
            <div className="flex items-center gap-2.5">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/25">
                <FileText className="h-4 w-4 text-white" />
              </div>
              <span className="text-sm font-semibold text-white tracking-tight">
                InvoiceAI
              </span>
            </div>
          )}
          {collapsed && (
            <div className="mx-auto flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/25">
              <FileText className="h-4 w-4 text-white" />
            </div>
          )}
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="hidden lg:flex h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
          >
            <ChevronLeft
              className={`h-4 w-4 transition-transform duration-300 ${collapsed ? 'rotate-180' : ''}`}
            />
          </button>
          <button
            onClick={() => setMobileOpen(false)}
            className="flex lg:hidden h-7 w-7 items-center justify-center rounded-md text-slate-400 hover:bg-white/5 hover:text-white transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              onClick={() => setMobileOpen(false)}
              className={({ isActive }) =>
                `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200
                ${
                  isActive
                    ? 'bg-gradient-to-r from-indigo-500/15 to-purple-500/10 text-white shadow-sm shadow-indigo-500/10 border border-indigo-500/20'
                    : 'text-slate-400 hover:bg-white/5 hover:text-white border border-transparent'
                }
                ${collapsed ? 'justify-center px-0' : ''}`
              }
            >
              <item.icon
                className={`h-[18px] w-[18px] shrink-0 transition-colors ${collapsed ? '' : ''}`}
              />
              {!collapsed && <span>{item.label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="border-t border-white/5 p-3">
          {!collapsed && user && (
            <div className="mb-2 rounded-lg bg-white/5 px-3 py-2">
              <p className="text-xs font-medium text-white truncate">
                {user.full_name || user.email}
              </p>
              <div className="flex items-center justify-between gap-1 mt-1">
                <p className="text-[10px] text-slate-400 truncate max-w-[120px]">{user.email}</p>
                <span className="text-[9px] uppercase px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-semibold border border-indigo-500/30 shrink-0">
                  {user.role?.replace('RoleEnum.', '')}
                </span>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-all duration-200 ${
              collapsed ? 'justify-center px-0' : ''
            }`}
          >
            <LogOut className="h-[18px] w-[18px] shrink-0" />
            {!collapsed && <span>Sign out</span>}
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar */}
        <header className="flex h-16 items-center gap-4 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 px-6">
          <button
            onClick={() => setMobileOpen(true)}
            className="flex lg:hidden h-9 w-9 items-center justify-center rounded-lg border border-border text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div className="flex-1" />
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

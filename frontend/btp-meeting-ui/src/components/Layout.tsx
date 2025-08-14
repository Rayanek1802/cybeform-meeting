import React from 'react'
import { useLocation, Link, useNavigate } from 'react-router-dom'
import { 
  Home,
  Video,
  FileText,
  Calendar,
  Users,
  BarChart3,
  Settings,
  Search,
  Bell,
  User,
  LogOut
} from 'lucide-react'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { Badge } from '../components/ui/badge'
import { useAuthStore } from '../store/authStore'
import { useToast } from '../components/ui/toaster'

interface LayoutProps {
  children: React.ReactNode
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const { addToast } = useToast()

  const handleLogout = () => {
    logout()
    addToast({
      title: 'Déconnexion',
      description: 'Vous avez été déconnecté avec succès',
      variant: 'success'
    })
    navigate('/login')
  }

  const navigationItems = [
    {
      icon: Home,
      label: 'Accueil',
      href: '/',
      active: location.pathname === '/',
      disabled: false
    },
    {
      icon: Video,
      label: 'CybeMeeting',
      href: '/',
      active: location.pathname.includes('/projects'),
      disabled: false
    },
    {
      icon: FileText,
      label: 'CybeAnalyse',
      href: '/rapports',
      active: false,
      disabled: true
    },
    {
      icon: FileText,
      label: 'CybeDocument',
      href: '/rapports',
      active: false,
      disabled: true
    },
    {
      icon: BarChart3,
      label: 'CybeBudget',
      href: '/analytics',
      active: false,
      disabled: true
    },
    {
      icon: Users,
      label: 'Équipe',
      href: '/equipe',
      active: false,
      disabled: true
    },
   
    {
      icon: Settings,
      label: 'Paramètres',
      href: '/parametres',
      active: false,
      disabled: true
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6">
          <div className="border-b border-gray-200 pb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl overflow-hidden shadow-lg">
                <img 
                  src="/logo.png" 
                  alt="Cybeform Logo" 
                  className="w-full h-full object-cover"
                />
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-[#4F46E5] to-[#C026D3] bg-clip-text text-transparent">
                Cybeform
              </h1>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon
            const isActive = item.active
            
            if (item.disabled) {
              return (
                <div
                  key={item.label}
                  className="flex items-center gap-3 px-3 py-2.5 text-gray-400 cursor-not-allowed rounded-lg"
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </div>
              )
            }

            return (
              <Link
                key={item.label}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span>{item.label}</span>
                {isActive && (
                  <div className="ml-auto w-2 h-2 bg-blue-600 rounded-full" />
                )}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-6">
          <div className="border-t border-gray-200 pt-4">
            <div className="text-xs text-gray-500">
              <div>Cybeform v1.0</div>
              <div>BTP Edition</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-semibold text-gray-900">
                {location.pathname === '/' ? 'Accueil' : 
                 location.pathname.includes('/projects') ? 'Meetings' : 'CybeMeeting'}
              </h1>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Rechercher..."
                  className="pl-10 w-80 bg-gray-50 border-gray-200 focus:bg-white"
                />
              </div>
              
              {/* User Info */}
              <div className="flex items-center gap-3 px-3 py-1.5 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] rounded-full">
                  <span className="text-white text-sm font-medium">
                    {user?.first_name?.[0]}{user?.last_name?.[0]}
                  </span>
                </div>
                <div className="text-sm">
                  <div className="font-medium text-gray-900">
                    {user?.first_name} {user?.last_name}
                  </div>
                  <div className="text-gray-500">{user?.email}</div>
                </div>
              </div>
              
              {/* Logout */}
              <Button 
                variant="ghost" 
                size="icon" 
                onClick={handleLogout}
                className="text-gray-500 hover:text-red-600"
                title="Se déconnecter"
              >
                <LogOut className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default Layout

import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster, ToasterProvider } from 'components/ui/toaster'
import { useAuthStore } from 'store/authStore'
import HomePage from 'pages/HomePage'
import ProjectDashboard from 'pages/ProjectDashboard'
import NewMeeting from 'pages/NewMeeting'
import MeetingDetail from 'pages/MeetingDetail'
import Login from 'pages/Login'
import Register from 'pages/Register'
import NotFound from 'pages/NotFound'

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated)
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  
  return <>{children}</>
}

// Public Route Component (redirect if authenticated)
const PublicRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = useAuthStore(state => state.isAuthenticated)
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />
  }
  
  return <>{children}</>
}

function App() {
  return (
    <ToasterProvider>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={
          <PublicRoute>
            <Login />
          </PublicRoute>
        } />
        <Route path="/register" element={
          <PublicRoute>
            <Register />
          </PublicRoute>
        } />
        
        {/* Protected Routes */}
        <Route path="/" element={
          <ProtectedRoute>
            <HomePage />
          </ProtectedRoute>
        } />
        <Route path="/projects/:projectId" element={
          <ProtectedRoute>
            <ProjectDashboard />
          </ProtectedRoute>
        } />
        <Route path="/projects/:projectId/meetings/new" element={
          <ProtectedRoute>
            <NewMeeting />
          </ProtectedRoute>
        } />
        <Route path="/projects/:projectId/meetings/:meetingId" element={
          <ProtectedRoute>
            <MeetingDetail />
          </ProtectedRoute>
        } />
        
        <Route path="*" element={<NotFound />} />
      </Routes>
      <Toaster />
    </ToasterProvider>
  )
}

export default App

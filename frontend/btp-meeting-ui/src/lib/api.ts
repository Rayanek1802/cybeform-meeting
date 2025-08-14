import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token to headers
    const authData = localStorage.getItem('cybeform-auth')
    if (authData) {
      const { token } = JSON.parse(authData).state
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

// Types
export interface Project {
  id: string
  name: string
  created_at: string
  meetings_count: number
}

// Removed MeetingType enum - replaced by custom user instructions

export interface Meeting {
  id: string
  title: string
  date: string
  expected_speakers: number
  ai_instructions?: string
  status: 'En attente' | 'En cours de traitement' | 'Terminé' | 'Erreur'
  progress: number
  duration?: number
  participants_detected: string[]
  audio_file?: string
  report_file?: string
  created_at: string
}

export interface ProcessingStatus {
  stage: 'upload' | 'diarization' | 'transcription' | 'report' | 'done' | 'error'
  progress: number
  message: string
  estimated_time_remaining?: number
}

export interface TranscriptSegment {
  speaker: string
  start_time: number
  end_time: number
  text: string
}

export interface MeetingPreview {
  report_html: string
  stats: Record<string, any>
  participants: string[]
  duration: number
  transcript: TranscriptSegment[]
}

// API Functions
export const projectsApi = {
  // Create a new project
  create: async (data: { name: string }): Promise<Project> => {
    const response = await api.post('/projects/', data)
    return response.data
  },

  // Get all projects
  list: async (): Promise<Project[]> => {
    const response = await api.get('/projects/')
    return response.data
  },

  // Get a specific project
  get: async (projectId: string): Promise<Project> => {
    const response = await api.get(`/projects/${projectId}`)
    return response.data
  },

  // Get project meetings
  getMeetings: async (projectId: string): Promise<Meeting[]> => {
    const response = await api.get(`/projects/${projectId}/meetings`)
    return response.data
  },

  // Update project
  update: async (projectId: string, data: { name: string }): Promise<Project> => {
    const response = await api.put(`/projects/${projectId}`, data)
    return response.data
  },

  // Delete project
  delete: async (projectId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/projects/${projectId}`)
    return response.data
  },
}

export const meetingsApi = {
  // Create a new meeting
  create: async (projectId: string, data: {
    title?: string
    date?: string
    expected_speakers: number
    ai_instructions?: string
  }): Promise<Meeting> => {
    const response = await api.post(`/meetings/${projectId}/meetings`, data)
    return response.data
  },

  // Upload audio file
  uploadAudio: async (
    meetingId: string, 
    projectId: string, 
    file: File,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<{ message: string; filename: string; size_mb: number; duration?: number }> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('project_id', projectId)

    const response = await api.post(`/meetings/${meetingId}/audio`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
    return response.data
  },

  // Start processing
  startProcessing: async (
    meetingId: string, 
    projectId: string,
    expectedSpeakers?: number
  ): Promise<{ message: string }> => {
    const data: any = {}
    if (expectedSpeakers) {
      data.expected_speakers = expectedSpeakers
    }

    const response = await api.post(`/meetings/${meetingId}/process`, data, {
      params: { project_id: projectId }
    })
    return response.data
  },

  // Get processing status
  getStatus: async (meetingId: string, projectId: string): Promise<ProcessingStatus> => {
    const response = await api.get(`/meetings/${meetingId}/status`, {
      params: { project_id: projectId }
    })
    return response.data
  },

  // Get meeting preview
  getPreview: async (meetingId: string, projectId: string): Promise<MeetingPreview> => {
    const response = await api.get(`/meetings/${meetingId}/preview`, {
      params: { project_id: projectId }
    })
    return response.data
  },

  // Download report
  downloadReport: async (meetingId: string, projectId: string): Promise<Blob> => {
    const response = await api.get(`/meetings/${meetingId}/report.docx`, {
      params: { project_id: projectId },
      responseType: 'blob'
    })
    return response.data
  },

  // Delete meeting
  delete: async (meetingId: string, projectId: string): Promise<{ message: string }> => {
    const response = await api.delete(`/meetings/${meetingId}`, {
      params: { project_id: projectId }
    })
    return response.data
  },

  // Update meeting
  update: async (meetingId: string, projectId: string, data: {
    title?: string
    expected_speakers?: number
    ai_instructions?: string
  }): Promise<Meeting> => {
    const response = await api.put(`/meetings/${meetingId}`, data, {
      params: { project_id: projectId }
    })
    return response.data
  },
}

// Authentication API
export interface AuthUser {
  id: string
  email: string
  first_name: string
  last_name: string
  company?: string
  created_at: string
  is_active: boolean
}

export interface AuthResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface LoginData {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
  company?: string
}

export const authApi = {
  login: async (data: LoginData): Promise<AuthResponse> => {
    const response = await api.post('/auth/login', data)
    return response.data
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await api.post('/auth/register', data)
    return response.data
  },

  me: async (): Promise<AuthUser> => {
    const response = await api.get('/auth/me')
    return response.data
  },

  logout: async (): Promise<{ message: string }> => {
    const response = await api.post('/auth/logout')
    return response.data
  }
}

export default api

import { create } from 'zustand'
import { devtools } from 'zustand/middleware'
import { Project, Meeting } from '../lib/api.ts'

interface AppState {
  // Projects
  projects: Project[]
  currentProject: Project | null
  
  // Meetings
  meetings: Meeting[]
  currentMeeting: Meeting | null
  
  // Cache timestamps (projectId -> timestamp)
  meetingsCache: Record<string, number>
  
  // UI State
  isLoading: boolean
  error: string | null
  
  // Actions
  setProjects: (projects: Project[]) => void
  setCurrentProject: (project: Project | null) => void
  addProject: (project: Project) => void
  
  setMeetings: (meetings: Meeting[], projectId?: string) => void
  setCurrentMeeting: (meeting: Meeting | null) => void
  addMeeting: (meeting: Meeting) => void
  updateMeeting: (meetingId: string, updates: Partial<Meeting>) => void
  deleteMeeting: (meetingId: string) => void
  updateMeetingsCache: (projectId: string) => void
  isMeetingsCacheValid: (projectId: string, maxAge?: number) => boolean
  
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  
  // Utility actions
  reset: () => void
}

const initialState = {
  projects: [],
  currentProject: null,
  meetings: [],
  currentMeeting: null,
  meetingsCache: {},
  isLoading: false,
  error: null,
}

export const useStore = create<AppState>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Project actions
      setProjects: (projects) => 
        set({ projects }, false, 'setProjects'),

      setCurrentProject: (project) => 
        set({ currentProject: project }, false, 'setCurrentProject'),

      addProject: (project) => 
        set(
          (state) => ({ 
            projects: [project, ...state.projects] 
          }),
          false,
          'addProject'
        ),

      // Meeting actions
      setMeetings: (meetings, projectId) => 
        set(
          (state) => ({
            meetings,
            meetingsCache: projectId 
              ? { ...state.meetingsCache, [projectId]: Date.now() }
              : state.meetingsCache
          }),
          false,
          'setMeetings'
        ),

      setCurrentMeeting: (meeting) => 
        set({ currentMeeting: meeting }, false, 'setCurrentMeeting'),

      addMeeting: (meeting) => 
        set(
          (state) => ({ 
            meetings: [meeting, ...state.meetings] 
          }),
          false,
          'addMeeting'
        ),

      updateMeeting: (meetingId, updates) => 
        set(
          (state) => ({
            meetings: state.meetings.map(meeting =>
              meeting.id === meetingId 
                ? { ...meeting, ...updates }
                : meeting
            ),
            currentMeeting: state.currentMeeting?.id === meetingId
              ? { ...state.currentMeeting, ...updates }
              : state.currentMeeting
          }),
          false,
          'updateMeeting'
        ),

      deleteMeeting: (meetingId) => 
        set(
          (state) => ({
            meetings: state.meetings.filter(meeting => meeting.id !== meetingId),
            currentMeeting: state.currentMeeting?.id === meetingId
              ? null
              : state.currentMeeting
          }),
          false,
          'deleteMeeting'
        ),

      updateMeetingsCache: (projectId) =>
        set(
          (state) => ({
            meetingsCache: { ...state.meetingsCache, [projectId]: Date.now() }
          }),
          false,
          'updateMeetingsCache'
        ),

      isMeetingsCacheValid: (projectId, maxAge = 300000) => { // 5 minutes by default
        const state = get()
        const timestamp = state.meetingsCache[projectId]
        if (!timestamp) return false
        return Date.now() - timestamp < maxAge
      },

      // UI actions
      setLoading: (loading) => 
        set({ isLoading: loading }, false, 'setLoading'),

      setError: (error) => 
        set({ error }, false, 'setError'),

      // Utility
      reset: () => 
        set(initialState, false, 'reset'),
    }),
    {
      name: 'cybermeeting-store',
    }
  )
)

// Selectors
export const useProjects = () => useStore((state) => state.projects)
export const useCurrentProject = () => useStore((state) => state.currentProject)
export const useMeetings = () => useStore((state) => state.meetings)
export const useCurrentMeeting = () => useStore((state) => state.currentMeeting)
export const useLoading = () => useStore((state) => state.isLoading)
export const useError = () => useStore((state) => state.error)

// Action selectors
export const useProjectActions = () => useStore((state) => ({
  setProjects: state.setProjects,
  setCurrentProject: state.setCurrentProject,
  addProject: state.addProject,
}))

export const useMeetingActions = () => useStore((state) => ({
  setMeetings: state.setMeetings,
  setCurrentMeeting: state.setCurrentMeeting,
  addMeeting: state.addMeeting,
  updateMeeting: state.updateMeeting,
  deleteMeeting: state.deleteMeeting,
  updateMeetingsCache: state.updateMeetingsCache,
  isMeetingsCacheValid: state.isMeetingsCacheValid,
}))

export const useUIActions = () => useStore((state) => ({
  setLoading: state.setLoading,
  setError: state.setError,
  reset: state.reset,
}))

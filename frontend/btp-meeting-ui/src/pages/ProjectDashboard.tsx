import React, { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { Plus, ArrowLeft, Calendar, Users, Clock, Download, Eye, MoreVertical, Edit3, Trash2, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'

import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { useToast } from '../components/ui/toaster'

import { projectsApi, meetingsApi, type Project, type Meeting } from '../lib/api'
import { useProjectActions, useMeetingActions, useUIActions, useMeetings } from '../store/useStore'
import { formatDate, formatDuration } from '../lib/utils'
import { DeleteMeetingDialog } from '../components/DeleteMeetingDialog'
import EditMeetingDialog from '../components/EditMeetingDialog'
import Layout from '../components/Layout'
import MeetingCard from '../components/MeetingCard'

const ProjectDashboard: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  // Dialog states
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; meeting: Meeting | null }>({
    open: false,
    meeting: null
  })
  const [editDialog, setEditDialog] = useState<{ open: boolean; meeting: Meeting | null }>({
    open: false,
    meeting: null
  })
  const [isDeleting, setIsDeleting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Use global store for meetings
  const meetings = useMeetings()
  const { setCurrentProject } = useProjectActions()
  const { 
    setMeetings: setStoreMeetings, 
    deleteMeeting, 
    updateMeeting,
    updateMeetingsCache,
    isMeetingsCacheValid 
  } = useMeetingActions()
  const { setError } = useUIActions()
  const { addToast } = useToast()

  useEffect(() => {
    if (projectId) {
      // Check if we have valid cached data for this project
      if (isMeetingsCacheValid(projectId) && meetings.length > 0) {
        // Use cached data, just load project info
        loadProjectInfo()
      } else {
        // Load fresh data
        loadProjectData()
      }
    }
  }, [projectId])

  const loadProjectInfo = async () => {
    if (!projectId) return

    try {
      setIsLoading(true)
      const projectData = await projectsApi.get(projectId)
      setProject(projectData)
      setCurrentProject(projectData)
    } catch (error) {
      console.error('Failed to load project info:', error)
      setError('Erreur lors du chargement du projet')
      addToast({
        title: 'Erreur',
        description: 'Impossible de charger les informations du projet',
        variant: 'error'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadProjectData = async () => {
    if (!projectId) return

    try {
      setIsLoading(true)
      
      // Load project and meetings in parallel
      const [projectData, meetingsData] = await Promise.all([
        projectsApi.get(projectId),
        projectsApi.getMeetings(projectId)
      ])
      
      setProject(projectData)
      setCurrentProject(projectData)
      setStoreMeetings(meetingsData, projectId)
      
    } catch (error) {
      console.error('Failed to load project data:', error)
      setError('Erreur lors du chargement du projet')
      addToast({
        title: 'Erreur',
        description: 'Impossible de charger les données du projet',
        variant: 'error'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDownloadReport = async (meeting: Meeting) => {
    if (!meeting.report_file || !projectId) return

    try {
      const blob = await meetingsApi.downloadReport(meeting.id, projectId)
      
      // Create download link
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${meeting.title}.docx`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      addToast({
        title: 'Succès',
        description: 'Rapport téléchargé avec succès',
        variant: 'success'
      })
    } catch (error) {
      console.error('Failed to download report:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de télécharger le rapport',
        variant: 'error'
      })
    }
  }

  const handleEditMeeting = (meeting: Meeting) => {
    // Vérifier que le meeting existe encore dans notre liste locale
    const currentMeeting = meetings.find(m => m.id === meeting.id)
    if (!currentMeeting) {
      addToast({
        title: 'Erreur',
        description: 'Ce meeting n\'existe plus',
        variant: 'error'
      })
      return
    }
    setEditDialog({ open: true, meeting: currentMeeting })
  }

  const handleDeleteMeeting = (meeting: Meeting) => {
    // Vérifier que le meeting existe encore dans notre liste locale
    const currentMeeting = meetings.find(m => m.id === meeting.id)
    if (!currentMeeting) {
      addToast({
        title: 'Erreur',
        description: 'Ce meeting n\'existe plus',
        variant: 'error'
      })
      return
    }
    setDeleteDialog({ open: true, meeting: currentMeeting })
  }

  const handleConfirmDelete = async () => {
    if (!deleteDialog.meeting || !projectId) return

    try {
      setIsDeleting(true)
      await meetingsApi.delete(deleteDialog.meeting.id, projectId)
      
      // Remove from global store
      deleteMeeting(deleteDialog.meeting.id)
      
      // Update cache timestamp
      updateMeetingsCache(projectId)
      
      addToast({
        title: 'Succès',
        description: 'Meeting supprimé avec succès',
        variant: 'success'
      })
      
      setDeleteDialog({ open: false, meeting: null })
    } catch (error: any) {
      console.error('Failed to delete meeting:', error)
      
      // Si le meeting n'existe pas (404), on le supprime de l'interface
      if (error.response?.status === 404) {
        deleteMeeting(deleteDialog.meeting!.id)
        updateMeetingsCache(projectId)
        
        addToast({
          title: 'Information',
          description: 'Ce meeting avait déjà été supprimé',
          variant: 'success'
        })
        setDeleteDialog({ open: false, meeting: null })
      } else {
        addToast({
          title: 'Erreur',
          description: 'Impossible de supprimer le meeting. Actualisation des données...',
          variant: 'error'
        })
        
        // Recharger les données depuis le serveur
        loadProjectData()
      }
    } finally {
      setIsDeleting(false)
    }
  }

  const handleSaveEdit = async (data: { title: string; expected_speakers: number; ai_instructions?: string }) => {
    if (!editDialog.meeting || !projectId) return

    try {
      setIsSaving(true)
      const updatedMeeting = await meetingsApi.update(editDialog.meeting.id, projectId, data)
      
      // Update global store
      updateMeeting(editDialog.meeting.id, updatedMeeting)
      
      // Update cache timestamp
      updateMeetingsCache(projectId)
      
      addToast({
        title: 'Succès',
        description: 'Meeting modifié avec succès',
        variant: 'success'
      })
      
      setEditDialog({ open: false, meeting: null })
    } catch (error: any) {
      console.error('Failed to update meeting:', error)
      
      // Si le meeting n'existe pas (404), on informe et recharge
      if (error.response?.status === 404) {
        addToast({
          title: 'Information',
          description: 'Ce meeting n\'existe plus. Actualisation des données...',
          variant: 'error'
        })
        
        // Recharger les données depuis le serveur
        loadProjectData()
        setEditDialog({ open: false, meeting: null })
      } else {
        addToast({
          title: 'Erreur',
          description: 'Impossible de modifier le meeting',
          variant: 'error'
        })
      }
    } finally {
      setIsSaving(false)
    }
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-24 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </Layout>
    )
  }

  if (!project) {
    return (
      <Layout>
        <div className="text-center py-20">
          <h1 className="text-2xl font-bold mb-4">Projet non trouvé</h1>
          <Button onClick={() => navigate('/')}>
            Retour à l'accueil
          </Button>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => navigate('/')}>
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
              <p className="text-gray-600">
                Créé le {formatDate(project.created_at)}
              </p>
            </div>
          </div>
          
          <Link to={`/projects/${projectId}/meetings/new`}>
            <Button className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 rounded-xl">
              <Plus className="h-4 w-4" />
              Nouveau meeting
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Meetings</CardTitle>
              <Calendar className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">{meetings.length}</div>
              <p className="text-xs text-gray-500">
                {meetings.filter(m => m.status === 'Terminé').length} terminés
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Temps Total</CardTitle>
              <Clock className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {formatDuration(
                  meetings
                    .filter(m => m.duration)
                    .reduce((total, m) => total + (m.duration || 0), 0)
                )}
              </div>
              <p className="text-xs text-gray-500">
                d'enregistrements
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Participants</CardTitle>
              <Users className="h-4 w-4 text-gray-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-gray-900">
                {new Set(
                  meetings.flatMap(m => m.participants_detected)
                ).size}
              </div>
              <p className="text-xs text-gray-500">
                uniques détectés
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Meetings List */}
        <div>
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-gray-900">Meetings récents</h2>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => loadProjectData()}
                disabled={isLoading}
                className="gap-2"
              >
                <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
                Actualiser
              </Button>
              {meetings.length > 0 && (
                <p className="text-gray-500">
                  {meetings.length} meeting{meetings.length > 1 ? 's' : ''}
                </p>
              )}
            </div>
          </div>

          {meetings.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="text-center py-20"
            >
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <Calendar className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Aucun meeting</h3>
              <p className="text-gray-600 mb-8">
                Créez votre premier meeting pour commencer l'analyse de vos réunions.
              </p>
              <Link to={`/projects/${projectId}/meetings/new`}>
                <Button className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 rounded-xl">
                  <Plus className="h-4 w-4" />
                  Créer un meeting
                </Button>
              </Link>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, staggerChildren: 0.1 }}
              className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6"
            >
              {meetings.map((meeting, index) => (
                <motion.div
                  key={meeting.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                >
                  <MeetingCard
                    meeting={meeting}
                    projectId={projectId!}
                    onEdit={handleEditMeeting}
                    onDelete={handleDeleteMeeting}
                    onDownload={handleDownloadReport}
                  />
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </div>

      {/* Dialogues */}
      <DeleteMeetingDialog
        meeting={deleteDialog.meeting}
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, meeting: null })}
        onConfirm={handleConfirmDelete}
        isDeleting={isDeleting}
      />

      <EditMeetingDialog
        meeting={editDialog.meeting}
        open={editDialog.open}
        onClose={() => setEditDialog({ open: false, meeting: null })}
        onSave={handleSaveEdit}
        isSaving={isSaving}
      />
    </Layout>
  )
}

export default ProjectDashboard
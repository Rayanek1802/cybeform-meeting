import React, { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Download, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'

import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Progress } from '../components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Input } from '../components/ui/input'
import { useToast } from '../components/ui/toaster'

import { meetingsApi, projectsApi, type Meeting, type ProcessingStatus, type MeetingPreview } from '../lib/api'
import { formatDate, formatDuration } from '../lib/utils'
import Layout from '../components/Layout'
import ReportFormatter from '../components/ReportFormatter'

const MeetingDetail: React.FC = () => {
  const { projectId, meetingId } = useParams<{ projectId: string; meetingId: string }>()
  const navigate = useNavigate()
  
  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [status, setStatus] = useState<ProcessingStatus | null>(null)
  const [preview, setPreview] = useState<MeetingPreview | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('report')

  const { addToast } = useToast()

  useEffect(() => {
    if (projectId && meetingId) {
      loadMeetingData()
    }
  }, [projectId, meetingId])

  useEffect(() => {
    let interval: NodeJS.Timeout | null = null
    
    if (meeting?.status === 'En cours de traitement') {
      interval = setInterval(() => {
        loadProcessingStatus()
      }, 2000) // Poll every 2 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [meeting?.status])

  const loadMeetingData = async () => {
    if (!projectId || !meetingId) return

    try {
      setIsLoading(true)
      
      // Get meeting from project meetings list
      const projectMeetings = await projectsApi.getMeetings(projectId)
      const currentMeeting = projectMeetings.find(m => m.id === meetingId)
      
      if (!currentMeeting) {
        addToast({
          title: 'Erreur',
          description: 'Meeting non trouvé',
          variant: 'error'
        })
        navigate(`/projects/${projectId}`)
        return
      }
      
      setMeeting(currentMeeting)
      
      // Load processing status
      await loadProcessingStatus()
      
      // If completed, load preview
      if (currentMeeting.status === 'Terminé') {
        await loadPreview()
      }
      
    } catch (error) {
      console.error('Failed to load meeting data:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de charger les données du meeting',
        variant: 'error'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const loadProcessingStatus = async () => {
    if (!projectId || !meetingId) return

    try {
      const statusData = await meetingsApi.getStatus(meetingId, projectId)
      setStatus(statusData)
    } catch (error) {
      console.error('Failed to load status:', error)
    }
  }

  const loadPreview = async () => {
    if (!projectId || !meetingId) return

    try {
      const previewData = await meetingsApi.getPreview(meetingId, projectId)
      setPreview(previewData)
    } catch (error) {
      console.error('Failed to load preview:', error)
    }
  }

  const handleDownloadReport = async () => {
    if (!meeting?.report_file || !projectId || !meetingId) return

    try {
      const blob = await meetingsApi.downloadReport(meetingId, projectId)
      
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

  const getBadgeVariant = (stage: string) => {
    switch (stage) {
      case 'done':
        return 'default'
      case 'processing':
        return 'secondary'
      case 'pending':
        return 'outline'
      case 'error':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  const getStageLabel = (stage: string) => {
    switch (stage) {
      case 'upload':
        return 'Upload'
      case 'diarization':
        return 'Diarisation'
      case 'transcription':
        return 'Transcription'
      case 'report':
        return 'Génération rapport'
      case 'done':
        return 'Terminé'
      case 'error':
        return 'Erreur'
      default:
        return 'En attente'
    }
  }


  if (isLoading) {
    return (
      <Layout>
        <div className="space-y-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="h-64 bg-gray-200 rounded-lg"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
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
            <Link to={`/projects/${projectId}`}>
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                {meeting?.title || 'Meeting Detail'}
              </h1>
              {meeting && (
                <p className="text-gray-600">
                  {formatDate(meeting.date)} • {meeting.duration ? formatDuration(meeting.duration) : 'Durée inconnue'}
                </p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={loadMeetingData}
              className="gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Actualiser
            </Button>
            
            {meeting?.status === 'Terminé' && meeting.report_file && (
              <Button
                onClick={handleDownloadReport}
                className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 rounded-xl"
              >
                <Download className="h-4 w-4" />
                Télécharger le rapport
              </Button>
            )}
          </div>
        </div>


        {/* Processing Progress */}
        {meeting?.status === 'En cours de traitement' && status && (
          <Card className="border-blue-200 bg-blue-50/50">
            <CardHeader>
              <CardTitle className="text-blue-900">Traitement en cours</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-800">Progression</span>
                <span className="text-sm font-medium text-blue-800">{status.progress}%</span>
              </div>
              <Progress value={status.progress} className="h-2" />
              <p className="text-sm text-blue-700">{status.message}</p>
              
              <div className="flex items-center gap-2 mt-4">
                <Badge variant="outline" className="bg-white border-blue-200">
                  {getStageLabel(status.stage)}
                </Badge>
                <span className="text-xs text-blue-600">Temps estimé : 2-3 minutes</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Content Tabs */}
        {meeting?.status === 'Terminé' && preview && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="report">Rapport</TabsTrigger>
                <TabsTrigger value="transcript">Transcription</TabsTrigger>
              </TabsList>
              
              <TabsContent value="report" className="space-y-0">
                <ReportFormatter htmlContent={preview.report_html} />
              </TabsContent>
              
              <TabsContent value="transcript" className="space-y-0">
                <Card className="border-gray-200">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Transcription complète</CardTitle>
                      <div className="relative">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                        <Input
                          placeholder="Rechercher dans la transcription..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-10 w-80"
                        />
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4 max-h-96 overflow-y-auto">
                      {filteredTranscript.map((segment, index) => (
                        <div key={index} className="border-l-4 border-blue-200 pl-4 py-2 bg-gray-50 rounded-r-lg">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge variant="outline" className="text-xs">
                              {segment.speaker}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {Math.floor(segment.start_time / 60)}:{String(Math.floor(segment.start_time % 60)).padStart(2, '0')} - 
                              {Math.floor(segment.end_time / 60)}:{String(Math.floor(segment.end_time % 60)).padStart(2, '0')}
                            </span>
                          </div>
                          <p className="text-sm text-gray-800">{segment.text}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </motion.div>
        )}
      </div>
    </Layout>
  )
}

export default MeetingDetail
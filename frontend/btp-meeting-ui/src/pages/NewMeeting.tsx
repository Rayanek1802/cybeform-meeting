import React, { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { ArrowLeft, Mic, Upload, Play } from 'lucide-react'
import { motion } from 'framer-motion'

import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs'
import { Textarea } from '../components/ui/textarea'
import { useToast } from '../components/ui/toaster'

import AudioRecorder from '../components/AudioRecorder'
import FileUpload from '../components/FileUpload'

import { meetingsApi } from '../lib'
import { useMeetingActions } from '../store/useStore'
import Layout from '../components/Layout'

const NewMeeting: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  
  const [title, setTitle] = useState('')
  const [expectedSpeakers, setExpectedSpeakers] = useState(2)
  const [aiInstructions, setAiInstructions] = useState('')
  const [audioSource, setAudioSource] = useState<'record' | 'upload'>('upload')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [recordedAudio, setRecordedAudio] = useState<{ blob: Blob; duration: number } | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isUploading, setIsUploading] = useState(false)

  const { addMeeting } = useMeetingActions()
  const { addToast } = useToast()

  const handleCreateMeeting = async () => {
    if (!projectId) return

    try {
      setIsCreating(true)

      // Generate title if not provided
      const meetingTitle = title.trim() || `Réunion du ${new Date().toLocaleDateString('fr-FR')}`

      // Create meeting
      const meeting = await meetingsApi.create(projectId, {
        title: meetingTitle,
        expected_speakers: expectedSpeakers,
        ai_instructions: aiInstructions.trim() || undefined
      })

      addMeeting(meeting)

      setIsUploading(true)

      // Upload audio
      let audioFile: File
      if (selectedFile) {
        audioFile = selectedFile
      } else if (recordedAudio) {
        // Convert blob to file
        audioFile = new File([recordedAudio.blob], `recording-${Date.now()}.webm`, {
          type: 'audio/webm'
        })
      } else {
        throw new Error('No audio data available')
      }

      await meetingsApi.uploadAudio(meeting.id, projectId, audioFile)

      // Start processing
      await meetingsApi.startProcessing(meeting.id, projectId, expectedSpeakers)

      addToast({
        title: 'Succès',
        description: 'Meeting créé et traitement lancé',
        variant: 'success'
      })

      // Navigate to meeting detail
      navigate(`/projects/${projectId}/meetings/${meeting.id}`)

    } catch (error) {
      console.error('Failed to create meeting:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de créer le meeting',
        variant: 'error'
      })
    } finally {
      setIsCreating(false)
      setIsUploading(false)
    }
  }

  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
  }

  const handleRecordingComplete = (blob: Blob, duration: number) => {
    setRecordedAudio({ blob, duration })
  }

  const canCreateMeeting = () => {
    if (isCreating || isUploading) return false
    if (audioSource === 'upload') return !!selectedFile
    if (audioSource === 'record') return !!recordedAudio
    return false
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link to={`/projects/${projectId}`}>
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-5 w-5" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Nouveau meeting</h1>
            <p className="text-gray-600">
              Créez et analysez votre réunion de chantier
            </p>
          </div>
        </div>

        {/* Main Content */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl"
        >
          <Card className="border-gray-200">
            <CardHeader>
              <CardTitle className="text-xl text-gray-900">Informations du meeting</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Meeting Info */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="title">Titre du meeting (optionnel)</Label>
                  <Input
                    id="title"
                    placeholder="Ex: Réunion chantier du 11/08/2025"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="speakers">Nombre d'intervenants attendus</Label>
                  <Input
                    id="speakers"
                    type="number"
                    min="1"
                    max="20"
                    value={expectedSpeakers}
                    onChange={(e) => setExpectedSpeakers(Number(e.target.value))}
                  />
                  <p className="text-xs text-gray-500">
                    Améliore la diarisation (séparation des voix)
                  </p>
                </div>
              </div>

              {/* AI Instructions */}
              <div className="space-y-2">
                <Label htmlFor="ai-instructions">Instructions pour l'IA (optionnel)</Label>
                <Textarea
                  id="ai-instructions"
                  placeholder="Ex: C'est une réunion de chantier, focalisez-vous sur les problèmes techniques et la sécurité. Mettez en avant nos solutions et minimisez les retards évoqués..."
                  value={aiInstructions}
                  onChange={(e) => setAiInstructions(e.target.value)}
                  rows={4}
                  className="resize-none"
                />
                <p className="text-xs text-gray-500">
                  Personnalisez l'analyse : type de réunion, éléments à prioriser, angle d'approche, etc.
                </p>
              </div>

              {/* Audio Source Selection */}
              <div className="space-y-4">
                <Label>Source audio</Label>
                <Tabs value={audioSource} onValueChange={(value) => setAudioSource(value as 'record' | 'upload')}>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="upload" className="gap-2">
                      <Upload className="h-4 w-4" />
                      Importer un fichier
                    </TabsTrigger>
                    <TabsTrigger value="record" className="gap-2">
                      <Mic className="h-4 w-4" />
                      Enregistrer maintenant
                    </TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="upload" className="mt-6">
                    <FileUpload
                      onFileSelect={handleFileSelect}
                      disabled={isCreating || isUploading}
                    />
                  </TabsContent>
                  
                  <TabsContent value="record" className="mt-6">
                    <AudioRecorder
                      onRecordingComplete={handleRecordingComplete}
                      disabled={isCreating || isUploading}
                    />
                  </TabsContent>
                </Tabs>
              </div>

              {/* Action Button */}
              <div className="flex justify-end pt-4">
                <Button
                  onClick={handleCreateMeeting}
                  disabled={!canCreateMeeting()}
                  size="lg"
                  className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 disabled:opacity-50 disabled:pointer-events-none rounded-xl"
                >
                  <Play className="h-4 w-4" />
                  {isCreating ? 'Création en cours...' : 'Lancer l\'analyse IA'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </Layout>
  )
}

export default NewMeeting
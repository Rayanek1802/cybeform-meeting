import React, { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { type Meeting } from '../lib/api'

interface EditMeetingDialogProps {
  meeting: Meeting | null
  open: boolean
  onClose: () => void
  onSave: (data: { title: string; expected_speakers: number; ai_instructions?: string }) => Promise<void>
  isSaving: boolean
}

const EditMeetingDialog: React.FC<EditMeetingDialogProps> = ({
  meeting,
  open,
  onClose,
  onSave,
  isSaving
}) => {
  const [title, setTitle] = useState('')
  const [expectedSpeakers, setExpectedSpeakers] = useState(2)
  const [aiInstructions, setAiInstructions] = useState('')

  useEffect(() => {
    if (meeting) {
      setTitle(meeting.title)
      setExpectedSpeakers(meeting.expected_speakers)
      setAiInstructions(meeting.ai_instructions || '')
    }
  }, [meeting])

  const handleSave = async () => {
    if (!title.trim()) return
    
    try {
      await onSave({
        title: title.trim(),
        expected_speakers: expectedSpeakers,
        ai_instructions: aiInstructions.trim() || undefined
      })
      onClose()
    } catch (error) {
      // Error handling is done in parent component
      console.error('Error saving meeting:', error)
    }
  }

  const handleClose = () => {
    if (meeting) {
      setTitle(meeting.title)
      setExpectedSpeakers(meeting.expected_speakers)
      setAiInstructions(meeting.ai_instructions || '')
    }
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Modifier le meeting</DialogTitle>
          <DialogDescription>
            Modifiez les informations de votre meeting.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="meeting-title">Titre du meeting</Label>
            <Input
              id="meeting-title"
              placeholder="Ex: Réunion chantier du 11/08/2025"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="speakers-edit">Nombre d'intervenants</Label>
              <Input
                id="speakers-edit"
                type="number"
                min="1"
                max="20"
                value={expectedSpeakers}
                onChange={(e) => setExpectedSpeakers(Number(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ai-instructions-edit">Instructions pour l'IA (optionnel)</Label>
              <Textarea
                id="ai-instructions-edit"
                placeholder="Ex: C'est une réunion de chantier, focalisez-vous sur les problèmes techniques et la sécurité..."
                value={aiInstructions}
                onChange={(e) => setAiInstructions(e.target.value)}
                rows={3}
                className="resize-none"
              />
              <p className="text-xs text-gray-500">
                Personnalisez l'analyse selon vos besoins
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isSaving}
          >
            Annuler
          </Button>
          <Button
            onClick={handleSave}
            disabled={!title.trim() || isSaving}
            className="bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none rounded-xl"
          >
            {isSaving ? 'Enregistrement...' : 'Enregistrer'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default EditMeetingDialog
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
import { type Project } from '../lib/api'

interface EditProjectDialogProps {
  project: Project | null
  open: boolean
  onClose: () => void
  onSave: (data: { name: string }) => Promise<void>
  isSaving: boolean
}

const EditProjectDialog: React.FC<EditProjectDialogProps> = ({
  project,
  open,
  onClose,
  onSave,
  isSaving
}) => {
  const [projectName, setProjectName] = useState('')

  useEffect(() => {
    if (project) {
      setProjectName(project.name)
    }
  }, [project])

  const handleSave = async () => {
    if (!projectName.trim()) return
    
    try {
      await onSave({ name: projectName.trim() })
      onClose()
    } catch (error) {
      // Error handling is done in parent component
      console.error('Error saving project:', error)
    }
  }

  const handleClose = () => {
    setProjectName(project?.name || '')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Modifier le projet</DialogTitle>
          <DialogDescription>
            Modifiez le nom de votre projet BTP.
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="project-name">Nom du projet</Label>
            <Input
              id="project-name"
              placeholder="Ex: Rénovation Immeuble Haussman"
              value={projectName}
              onChange={(e) => setProjectName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && projectName.trim()) {
                  handleSave()
                }
              }}
            />
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
            disabled={!projectName.trim() || isSaving}
            className="bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none rounded-xl"
          >
            {isSaving ? 'Enregistrement...' : 'Enregistrer'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default EditProjectDialog

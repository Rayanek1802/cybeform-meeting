import React from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '../components/ui/dialog'
import { Button } from '../components/ui/button'
import { AlertTriangle } from 'lucide-react'
import { type Project } from '../lib/api.ts'

interface DeleteProjectDialogProps {
  project: Project | null
  open: boolean
  onClose: () => void
  onConfirm: () => Promise<void>
  isDeleting: boolean
}

const DeleteProjectDialog: React.FC<DeleteProjectDialogProps> = ({
  project,
  open,
  onClose,
  onConfirm,
  isDeleting
}) => {
  const handleConfirm = async () => {
    try {
      await onConfirm()
      onClose()
    } catch (error) {
      // Error handling is done in parent component
      console.error('Error deleting project:', error)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            Supprimer le projet
          </DialogTitle>
          <DialogDescription>
            Cette action est irréversible. Tous les meetings et rapports de ce projet seront définitivement supprimés.
          </DialogDescription>
        </DialogHeader>
        
        <div className="py-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-sm text-red-800">
              <strong>Projet à supprimer :</strong> {project?.name}
            </p>
            <p className="text-xs text-red-600 mt-2">
              Cette action supprimera définitivement le projet et tous ses contenus.
            </p>
          </div>
        </div>
        
        <div className="flex justify-end space-x-2">
          <Button
            variant="outline"
            onClick={onClose}
            disabled={isDeleting}
          >
            Annuler
          </Button>
          <Button
            onClick={handleConfirm}
            disabled={isDeleting}
            variant="destructive"
            className="bg-red-600 hover:bg-red-700"
          >
            {isDeleting ? 'Suppression...' : 'Supprimer définitivement'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default DeleteProjectDialog

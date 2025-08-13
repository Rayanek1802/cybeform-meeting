import React from 'react'
import { AlertTriangle } from 'lucide-react'

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog'
import { Button } from '../components/ui/button'
import { type Meeting } from '../lib/api'

interface DeleteMeetingDialogProps {
  meeting: Meeting | null
  open: boolean
  onClose: () => void
  onConfirm: () => void
  isDeleting?: boolean
}

export const DeleteMeetingDialog: React.FC<DeleteMeetingDialogProps> = ({
  meeting,
  open,
  onClose,
  onConfirm,
  isDeleting = false
}) => {
  if (!meeting) return null

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-10 h-10 bg-red-50 rounded-full flex items-center justify-center">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>
            <div>
              <DialogTitle className="text-left">
                Supprimer le meeting
              </DialogTitle>
              <DialogDescription className="text-left">
                Cette action est irréversible.
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="py-4">
          <p className="text-sm text-muted-foreground mb-4">
            Vous êtes sur le point de supprimer définitivement le meeting :
          </p>
          
          <div className="bg-muted/50 rounded-lg p-4 border-l-4 border-red-500">
            <div className="font-medium text-sm">{meeting.title}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Créé le {new Date(meeting.created_at).toLocaleDateString('fr-FR')}
            </div>
          </div>

          <div className="mt-4 text-sm text-muted-foreground space-y-1">
            <p>• Tous les fichiers audio seront supprimés</p>
            <p>• Le rapport et la transcription seront perdus</p>
            <p>• Cette action ne peut pas être annulée</p>
          </div>
        </div>

        <DialogFooter>
          <Button 
            variant="outline" 
            onClick={onClose}
            disabled={isDeleting}
          >
            Annuler
          </Button>
          <Button 
            variant="destructive" 
            onClick={onConfirm}
            disabled={isDeleting}
            className="min-w-[100px]"
          >
            {isDeleting ? 'Suppression...' : 'Supprimer'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

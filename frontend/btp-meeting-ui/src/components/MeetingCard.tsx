import React from 'react'
import { Link } from 'react-router-dom'
import { 
  Eye, 
  Download, 
  Edit3, 
  Trash2, 
  MoreVertical, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Users,
  Calendar,
  Pause
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'

import { type Meeting } from '../lib/api'
import { formatDate, formatDuration } from '../lib/utils'

interface MeetingCardProps {
  meeting: Meeting
  projectId: string
  onEdit: (meeting: Meeting) => void
  onDelete: (meeting: Meeting) => void
  onDownload: (meeting: Meeting) => void
}

const MeetingCard: React.FC<MeetingCardProps> = ({
  meeting,
  projectId,
  onEdit,
  onDelete,
  onDownload
}) => {
  const getStatusConfig = (status: Meeting['status']) => {
    switch (status) {
      case 'Terminé':
        return {
          badge: 'Terminé',
          badgeVariant: 'default' as const,
          badgeClassName: 'bg-green-50 text-green-700 border-green-200',
          icon: CheckCircle,
          iconClassName: 'text-green-600',
          showProgress: false
        }
      case 'En cours de traitement':
        return {
          badge: 'En cours de traitement',
          badgeVariant: 'secondary' as const,
          badgeClassName: 'bg-blue-50 text-blue-700 border-blue-200',
          icon: Clock,
          iconClassName: 'text-blue-600',
          showProgress: true
        }
      case 'En attente':
        return {
          badge: 'En attente',
          badgeVariant: 'outline' as const,
          badgeClassName: 'bg-gray-50 text-gray-700 border-gray-200',
          icon: Pause,
          iconClassName: 'text-gray-500',
          showProgress: false
        }
      case 'Erreur':
        return {
          badge: 'Erreur',
          badgeVariant: 'destructive' as const,
          badgeClassName: 'bg-red-50 text-red-700 border-red-200',
          icon: AlertCircle,
          iconClassName: 'text-red-600',
          showProgress: false
        }
      default:
        return {
          badge: status,
          badgeVariant: 'outline' as const,
          badgeClassName: 'bg-gray-50 text-gray-700 border-gray-200',
          icon: Pause,
          iconClassName: 'text-gray-500',
          showProgress: false
        }
    }
  }

  const statusConfig = getStatusConfig(meeting.status)
  const StatusIcon = statusConfig.icon

  return (
    <Card className="hover:shadow-md transition-shadow duration-200 border-gray-200">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center">
              <StatusIcon className={`w-5 h-5 ${statusConfig.iconClassName}`} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-semibold text-gray-900 truncate">{meeting.title}</h3>
              <p className="text-sm text-gray-500">
                {formatDate(meeting.date)}
                {meeting.duration && (
                  <span className="ml-2">• {formatDuration(meeting.duration)}</span>
                )}
              </p>
            </div>
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuItem onClick={() => onEdit(meeting)}>
                <Edit3 className="mr-2 h-4 w-4" />
                Modifier
              </DropdownMenuItem>
              
              {meeting.status === 'Terminé' && (
                <Link to={`/projects/${projectId}/meetings/${meeting.id}`}>
                  <DropdownMenuItem>
                    <Eye className="mr-2 h-4 w-4" />
                    Consulter
                  </DropdownMenuItem>
                </Link>
              )}
              
              <DropdownMenuSeparator />
              <DropdownMenuItem 
                onClick={() => onDelete(meeting)}
                className="text-red-600 focus:text-red-600"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Supprimer
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        {/* Status Badge */}
        <div className="mb-4">
          <Badge 
            variant={statusConfig.badgeVariant}
            className={statusConfig.badgeClassName}
          >
            {statusConfig.badge}
          </Badge>
        </div>

        {/* Progress Bar for Processing */}
        {statusConfig.showProgress && meeting.progress_percentage !== undefined && (
          <div className="mb-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600">Progression du traitement</span>
              <span className="font-medium text-gray-900">{meeting.progress_percentage}%</span>
            </div>
            <Progress value={meeting.progress_percentage} className="h-2" />
            <p className="text-xs text-gray-500 mt-1">
              Transcription et analyse en cours... Temps estimé : 2-3 minutes
            </p>
          </div>
        )}

        {/* Success Message for Completed */}
        {meeting.status === 'Terminé' && (
          <div className="mb-4 p-3 bg-green-50 rounded-lg border border-green-200">
            <p className="text-sm text-green-800">
              <CheckCircle className="w-4 h-4 inline mr-1" />
              Rapport généré avec succès
            </p>
            <p className="text-xs text-green-600 mt-1">
              Le rapport de meeting est prêt et inclut la transcription complète, les décisions prises et le plan d'action.
            </p>
          </div>
        )}

        {/* Participants Info */}
        {meeting.participants_detected.length > 0 && (
          <div className="flex items-center gap-4 text-sm text-gray-500 mb-4">
            <div className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              <span>{meeting.participants_detected.length} participant{meeting.participants_detected.length > 1 ? 's' : ''}</span>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          {meeting.status === 'Terminé' && (
            <>
              <Link to={`/projects/${projectId}/meetings/${meeting.id}`} className="flex-1">
                <Button variant="outline" size="sm" className="w-full">
                  <Eye className="w-4 h-4 mr-2" />
                  Aperçu
                </Button>
              </Link>
              
              {meeting.report_file && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onDownload(meeting)}
                >
                  <Download className="w-4 h-4 mr-2" />
                  Télécharger
                </Button>
              )}
            </>
          )}
          
          {meeting.status === 'En cours de traitement' && (
            <Link to={`/projects/${projectId}/meetings/${meeting.id}`} className="flex-1">
              <Button variant="outline" size="sm" className="w-full">
                <Eye className="w-4 h-4 mr-2" />
                Suivre
              </Button>
            </Link>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default MeetingCard

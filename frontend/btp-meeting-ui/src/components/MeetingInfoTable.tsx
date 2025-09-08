import React from 'react'
import { Clock, Users, FileText, Calendar, Building, Settings, BarChart3, CheckCircle2 } from 'lucide-react'
import { Badge } from './ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { formatDate, formatDuration } from '../lib/utils'
import { Meeting } from '../lib/api'

interface MeetingInfoTableProps {
  meeting: Meeting
}

const MeetingInfoTable: React.FC<MeetingInfoTableProps> = ({ meeting }) => {
  const infoRows = [
    {
      id: 'date',
      label: 'Date & Heure',
      value: formatDate(meeting.date),
      icon: <Calendar className="h-4 w-4" />,
      highlight: false,
      category: 'Planification'
    },
    {
      id: 'duration',
      label: 'Durée totale',
      value: meeting.duration ? formatDuration(meeting.duration) : 'Non définie',
      icon: <Clock className="h-4 w-4" />,
      highlight: false,
      category: 'Planification'
    },
    {
      id: 'participants',
      label: 'Participants détectés',
      value: (
        <div className="flex flex-wrap gap-1">
          {meeting.participants_detected.map((participant, index) => (
            <Badge 
              key={index} 
              variant="secondary" 
              className="bg-blue-100 text-blue-800 border-blue-200 text-xs px-2 py-1"
            >
              {participant}
            </Badge>
          ))}
          <Badge 
            variant="outline" 
            className="bg-gray-50 text-gray-600 border-gray-300 text-xs px-2 py-1 ml-1"
          >
            {meeting.participants_detected.length} total
          </Badge>
        </div>
      ),
      icon: <Users className="h-4 w-4" />,
      highlight: true,
      category: 'Participants'
    },
    {
      id: 'status',
      label: 'Statut du traitement',
      value: (
        <div className="flex items-center gap-2">
          <Badge 
            variant={meeting.status === 'Terminé' ? 'default' : 'secondary'}
            className={
              meeting.status === 'Terminé' 
                ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white border-none shadow-sm'
                : meeting.status === 'En cours de traitement'
                ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white border-none shadow-sm animate-pulse'
                : 'bg-gradient-to-r from-gray-400 to-gray-500 text-white border-none shadow-sm'
            }
          >
            {meeting.status === 'Terminé' && <CheckCircle2 className="h-3 w-3 mr-1" />}
            {meeting.status}
          </Badge>
          {meeting.status === 'Terminé' && meeting.report_file && (
            <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200 text-xs">
              Rapport disponible
            </Badge>
          )}
        </div>
      ),
      icon: <BarChart3 className="h-4 w-4" />,
      highlight: meeting.status === 'Terminé',
      category: 'Traitement'
    },
    {
      id: 'project',
      label: 'Nom du projet',
      value: meeting.project_name || 'Non spécifié',
      icon: <Building className="h-4 w-4" />,
      highlight: false,
      category: 'Projet'
    },
    {
      id: 'title',
      label: 'Titre de la réunion',
      value: meeting.title,
      icon: <FileText className="h-4 w-4" />,
      highlight: false,
      category: 'Détails'
    }
  ]

  // Ajouter les instructions IA si présentes
  if (meeting.ai_instructions) {
    infoRows.push({
      id: 'instructions',
      label: 'Instructions IA',
      value: (
        <div className="max-w-md">
          <p className="text-sm text-gray-700 italic bg-gradient-to-r from-purple-50 to-pink-50 p-2 rounded-lg border border-purple-200">
            "{meeting.ai_instructions}"
          </p>
        </div>
      ),
      icon: <Settings className="h-4 w-4" />,
      highlight: false,
      category: 'Configuration'
    })
  }

  return (
    <Card className="border-gray-200 shadow-lg">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-3 text-xl">
          <div className="p-2 rounded-lg bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-md">
            <FileText className="h-5 w-5" />
          </div>
          Informations détaillées
          <Badge 
            variant="outline" 
            className="bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border-blue-200 ml-auto"
          >
            {infoRows.length} propriétés
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40%]">Propriété</TableHead>
              <TableHead className="w-[60%]">Valeur</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {infoRows.map((row) => (
              <TableRow 
                key={row.id} 
                highlight={row.highlight}
                className={row.highlight ? "bg-gradient-to-r from-blue-50 to-indigo-50" : ""}
              >
                <TableCell 
                  icon={row.icon}
                  className="font-semibold"
                >
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {row.label}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      {row.category}
                    </div>
                  </div>
                </TableCell>
                <TableCell highlight={row.highlight}>
                  {typeof row.value === 'string' ? (
                    <span className={row.highlight ? "font-semibold text-blue-800" : "text-gray-700"}>
                      {row.value}
                    </span>
                  ) : (
                    row.value
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        
        {/* Footer avec statistiques rapides */}
        <div className="bg-gradient-to-r from-gray-50 to-blue-50 p-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                Prêt pour analyse
              </span>
              <span>ID: {meeting.id.substring(0, 8)}...</span>
            </div>
            <div className="flex items-center gap-2">
              <span>Créé le {formatDate(meeting.date)}</span>
              {meeting.status === 'Terminé' && (
                <Badge variant="outline" className="bg-green-100 text-green-700 border-green-300">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  Traitement terminé
                </Badge>
              )}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default MeetingInfoTable
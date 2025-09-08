import React from 'react'
import { Search, Clock, User, Volume2 } from 'lucide-react'
import { Badge } from './ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'

interface TranscriptSegment {
  speaker: string
  text: string
  start_time: number
  end_time: number
  confidence?: number
}

interface TranscriptTableProps {
  segments: TranscriptSegment[]
  searchTerm: string
  onSearchChange: (term: string) => void
}

const TranscriptTable: React.FC<TranscriptTableProps> = ({ 
  segments, 
  searchTerm, 
  onSearchChange 
}) => {
  const filteredSegments = segments.filter(segment =>
    segment.text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    segment.speaker.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const formatTime = (timeInSeconds: number) => {
    const minutes = Math.floor(timeInSeconds / 60)
    const seconds = Math.floor(timeInSeconds % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  const getDuration = (start: number, end: number) => {
    return Math.floor(end - start)
  }

  const getSpeakerColor = (speaker: string) => {
    const colors = [
      'bg-blue-100 text-blue-800 border-blue-200',
      'bg-green-100 text-green-800 border-green-200',
      'bg-purple-100 text-purple-800 border-purple-200',
      'bg-orange-100 text-orange-800 border-orange-200',
      'bg-pink-100 text-pink-800 border-pink-200',
      'bg-indigo-100 text-indigo-800 border-indigo-200',
    ]
    
    let hash = 0
    for (let i = 0; i < speaker.length; i++) {
      hash = speaker.charCodeAt(i) + ((hash << 5) - hash)
    }
    
    return colors[Math.abs(hash) % colors.length]
  }

  const getTotalDuration = () => {
    if (segments.length === 0) return 0
    return Math.max(...segments.map(s => s.end_time))
  }

  const getUniquespeakers = () => {
    return [...new Set(segments.map(s => s.speaker))]
  }

  return (
    <Card className="border-gray-200 shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-md">
              <Volume2 className="h-5 w-5" />
            </div>
            Transcription complète
            <div className="flex items-center gap-2 ml-4">
              <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                {filteredSegments.length} segments
              </Badge>
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {getUniquespeakers().length} intervenants
              </Badge>
              <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200">
                {formatTime(getTotalDuration())} total
              </Badge>
            </div>
          </CardTitle>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <Input
              placeholder="Rechercher dans la transcription..."
              value={searchTerm}
              onChange={(e) => onSearchChange(e.target.value)}
              className="pl-10 w-80 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 rounded-lg"
            />
          </div>
        </div>
        
        {searchTerm && (
          <div className="text-sm text-gray-600">
            {filteredSegments.length} résultat{filteredSegments.length !== 1 ? 's' : ''} 
            {filteredSegments.length !== segments.length && ` sur ${segments.length} segments`}
          </div>
        )}
      </CardHeader>
      
      <CardContent className="p-0">
        <div className="max-h-96 overflow-y-auto">
          <Table>
            <TableHeader className="sticky top-0 z-10">
              <TableRow>
                <TableHead className="w-[80px]">Temps</TableHead>
                <TableHead className="w-[120px]">Intervenant</TableHead>
                <TableHead className="w-[60px]">Durée</TableHead>
                <TableHead>Contenu</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSegments.map((segment, index) => (
                <TableRow 
                  key={index}
                  className="group hover:bg-gradient-to-r hover:from-gray-50 hover:to-blue-50 transition-all duration-200"
                >
                  <TableCell 
                    icon={<Clock className="h-3 w-3" />}
                    className="font-mono text-xs"
                  >
                    <div className="text-gray-600">
                      <div className="font-medium">{formatTime(segment.start_time)}</div>
                      <div className="text-gray-400 text-xs">
                        - {formatTime(segment.end_time)}
                      </div>
                    </div>
                  </TableCell>
                  
                  <TableCell>
                    <Badge 
                      variant="outline" 
                      className={`${getSpeakerColor(segment.speaker)} font-medium text-xs px-3 py-1`}
                    >
                      <User className="h-3 w-3 mr-1" />
                      {segment.speaker}
                    </Badge>
                  </TableCell>
                  
                  <TableCell className="text-xs text-gray-500 font-mono">
                    {getDuration(segment.start_time, segment.end_time)}s
                  </TableCell>
                  
                  <TableCell className="max-w-md">
                    <div className="text-sm text-gray-800 leading-relaxed">
                      {searchTerm ? (
                        <span
                          dangerouslySetInnerHTML={{
                            __html: segment.text.replace(
                              new RegExp(searchTerm, 'gi'),
                              '<mark class="bg-yellow-200 px-1 rounded">$&</mark>'
                            )
                          }}
                        />
                      ) : (
                        segment.text
                      )}
                    </div>
                    {segment.confidence && (
                      <div className="mt-1">
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            segment.confidence > 0.8 
                              ? 'bg-green-50 text-green-700 border-green-200'
                              : segment.confidence > 0.6
                              ? 'bg-yellow-50 text-yellow-700 border-yellow-200'
                              : 'bg-red-50 text-red-700 border-red-200'
                          }`}
                        >
                          {(segment.confidence * 100).toFixed(0)}% confiance
                        </Badge>
                      </div>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
        
        {filteredSegments.length === 0 && searchTerm && (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <Search className="h-12 w-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun résultat trouvé</h3>
            <p className="text-gray-500 text-center max-w-md">
              Aucun segment ne correspond à votre recherche "{searchTerm}". 
              Essayez avec d'autres mots-clés.
            </p>
          </div>
        )}
        
        {/* Footer avec statistiques */}
        <div className="bg-gradient-to-r from-gray-50 to-green-50 p-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                Transcription complète
              </span>
              <span>Durée totale: {formatTime(getTotalDuration())}</span>
            </div>
            <div className="flex items-center gap-2">
              <span>Intervenants: {getUniquespeakers().join(', ')}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default TranscriptTable
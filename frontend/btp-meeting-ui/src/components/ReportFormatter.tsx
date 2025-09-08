import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Badge } from './ui/badge'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'
import { FileText, Users, Lightbulb, CheckCircle, AlertTriangle, Clock } from 'lucide-react'

interface ParsedReportData {
  decisions: Array<{
    decision: string
    context?: string
    contexteTemporel?: string
  }>
  technicalDetails: Array<{
    detail: string
    context?: string
    contexteTemporel?: string
  }>
  risks: Array<{
    risk: string
    context?: string
    contexteTemporel?: string
  }>
  recommendations: Array<{
    recommendation: string
    context?: string
    contexteTemporel?: string
  }>
  keyPoints: Array<{
    point: string
    context?: string
    contexteTemporel?: string
  }>
  participants: Array<{
    participant: string
    role?: string
    context?: string
  }>
}

const parseReportHTML = (htmlContent: string): ParsedReportData => {
  const result: ParsedReportData = {
    decisions: [],
    technicalDetails: [],
    risks: [],
    recommendations: [],
    keyPoints: [],
    participants: []
  }

  // Regex patterns to extract dictionary-like structures
  const sectionPatterns = {
    decisions: /Decisions?\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis,
    technicalDetails: /Technical\s*details?\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis,
    risks: /Risks?\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis,
    recommendations: /Recommendations?\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis,
    keyPoints: /(?:Key\s*points?|Points?\s*cl[eé]s?)\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis,
    participants: /Participants?\s*[:\n]\s*(.*?)(?=\n\s*[A-Z][a-z]+:|$)/gis
  }

  // Dictionary pattern to extract individual items
  const dictPattern = /\{'([^']*)':\s*'([^']*)'/g

  Object.entries(sectionPatterns).forEach(([key, pattern]) => {
    const matches = htmlContent.match(pattern)
    if (matches) {
      matches.forEach(match => {
        let dictMatch
        while ((dictMatch = dictPattern.exec(match)) !== null) {
          const [, field, value] = dictMatch
          
          if (field === 'decision' && key === 'decisions') {
            result.decisions.push({ decision: value })
          } else if (field === 'detail' && key === 'technicalDetails') {
            result.technicalDetails.push({ detail: value })
          } else if (field === 'risk' && key === 'risks') {
            result.risks.push({ risk: value })
          } else if (field === 'recommendation' && key === 'recommendations') {
            result.recommendations.push({ recommendation: value })
          } else if (field === 'point' && key === 'keyPoints') {
            result.keyPoints.push({ point: value })
          } else if (field === 'participant' && key === 'participants') {
            result.participants.push({ participant: value })
          }
        }
      })
    }
  })

  return result
}

const formatTimeContext = (timeStr?: string) => {
  if (!timeStr) return null
  const match = timeStr.match(/\[(\d{2}:\d{2})-(\d{2}:\d{2})\]/)
  if (match) {
    return `${match[1]} - ${match[2]}`
  }
  return timeStr
}

interface ReportFormatterProps {
  htmlContent: string
}

const ReportFormatter: React.FC<ReportFormatterProps> = ({ htmlContent }) => {
  const parsedData = parseReportHTML(htmlContent)

  const sections = [
    {
      title: 'Décisions Clés',
      icon: CheckCircle,
      data: parsedData.decisions,
      color: 'from-green-500 to-emerald-600',
      bgColor: 'bg-green-50',
      textColor: 'text-green-700',
      field: 'decision'
    },
    {
      title: 'Détails Techniques',
      icon: FileText,
      data: parsedData.technicalDetails,
      color: 'from-blue-500 to-indigo-600',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-700',
      field: 'detail'
    },
    {
      title: 'Risques Identifiés',
      icon: AlertTriangle,
      data: parsedData.risks,
      color: 'from-red-500 to-rose-600',
      bgColor: 'bg-red-50',
      textColor: 'text-red-700',
      field: 'risk'
    },
    {
      title: 'Recommandations',
      icon: Lightbulb,
      data: parsedData.recommendations,
      color: 'from-yellow-500 to-amber-600',
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-700',
      field: 'recommendation'
    },
    {
      title: 'Points Clés',
      icon: Users,
      data: parsedData.keyPoints,
      color: 'from-purple-500 to-violet-600',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-700',
      field: 'point'
    }
  ]

  return (
    <div className="space-y-8">
      {sections.map((section, index) => {
        if (!section.data || section.data.length === 0) return null
        
        const Icon = section.icon
        
        return (
          <Card key={index} className={`border-2 border-gray-100 shadow-lg ${section.bgColor}/30`}>
            <CardHeader className={`${section.bgColor} border-b-2 border-gray-100`}>
              <CardTitle className={`flex items-center gap-3 ${section.textColor} text-lg font-bold`}>
                <div className={`p-2 rounded-lg bg-gradient-to-r ${section.color} text-white shadow-md`}>
                  <Icon className="h-5 w-5" />
                </div>
                {section.title}
                <Badge variant="outline" className={`ml-auto ${section.textColor} border-current`}>
                  {section.data.length} élément{section.data.length > 1 ? 's' : ''}
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead className="font-bold text-gray-700">Description</TableHead>
                    <TableHead className="font-bold text-gray-700 w-32">Contexte</TableHead>
                    <TableHead className="font-bold text-gray-700 w-28">
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        Temps
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {section.data.map((item: any, itemIndex) => (
                    <TableRow key={itemIndex} className="hover:bg-gray-50/70">
                      <TableCell className="font-medium text-gray-800 py-4">
                        <div className="flex items-start gap-2">
                          <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${section.color} mt-2 flex-shrink-0`} />
                          <span className="leading-relaxed">{item[section.field]}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-600 py-4">
                        {item.context && (
                          <div className="text-sm bg-gray-100 p-2 rounded-md italic">
                            {item.context}
                          </div>
                        )}
                      </TableCell>
                      <TableCell className="py-4">
                        {item.contexteTemporel && (
                          <Badge variant="outline" className="text-xs font-mono bg-blue-50 text-blue-700 border-blue-200">
                            {formatTimeContext(item.contexteTemporel)}
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )
      })}
      
      {parsedData.participants.length > 0 && (
        <Card className="border-2 border-gray-100 shadow-lg bg-indigo-50/30">
          <CardHeader className="bg-indigo-50 border-b-2 border-gray-100">
            <CardTitle className="flex items-center gap-3 text-indigo-700 text-lg font-bold">
              <div className="p-2 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white shadow-md">
                <Users className="h-5 w-5" />
              </div>
              Participants
              <Badge variant="outline" className="ml-auto text-indigo-700 border-current">
                {parsedData.participants.length} participant{parsedData.participants.length > 1 ? 's' : ''}
              </Badge>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {parsedData.participants.map((participant, index) => (
                <div key={index} className="flex items-center gap-3 p-3 bg-white rounded-lg border border-indigo-200 shadow-sm">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                    {participant.participant.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-800">{participant.participant}</p>
                    {participant.role && (
                      <p className="text-sm text-gray-600">{participant.role}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
      
      {/* Fallback for unstructured content */}
      {sections.every(s => !s.data || s.data.length === 0) && parsedData.participants.length === 0 && (
        <Card className="border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-gray-600" />
              Rapport d'analyse
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div 
              className="prose prose-sm max-w-none text-gray-800"
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ReportFormatter
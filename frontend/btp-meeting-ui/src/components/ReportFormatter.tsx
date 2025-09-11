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

  // Regex patterns to extract dictionary-like structures - more flexible patterns
  const sectionPatterns = {
    decisions: /(?:Decisions?|Décisions?)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis,
    technicalDetails: /(?:Technical\s*details?|Détails?\s*techniques?|Technicaldetails)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis,
    risks: /(?:Risks?|Risques?)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis,
    recommendations: /(?:Recommendations?|Recommandations?)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis,
    keyPoints: /(?:Key\s*points?|Points?\s*cl[eé]s?|Points?\s*importants?)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis,
    participants: /(?:Participants?)\s*[:\n]\s*(.*?)(?=\n\s*(?:[A-Z][a-z]+:|$))/gis
  }

  // Enhanced dictionary pattern to extract complete dictionary objects
  const parseDictString = (text: string): Record<string, string> => {
    const dict: Record<string, string> = {}
    
    // Multiple approaches to extract dictionary data
    
    // Approach 1: Try to extract a complete dictionary structure
    const fullDictMatch = text.match(/\{[^}]+\}/)
    if (fullDictMatch) {
      const dictContent = fullDictMatch[0]
      // Extract all key-value pairs from the dictionary with more flexible patterns
      const patterns = [
        /'([^']+)':\s*'([^']*)'/g,  // 'key': 'value'
        /"([^"]+)":\s*"([^"]*)"/g,  // "key": "value"  
        /['"]([^'"]+)['"]:\s*['"]([^'"]*)['"](?:,|\})/g  // More flexible quotes
      ]
      
      for (const pattern of patterns) {
        let match
        while ((match = pattern.exec(dictContent)) !== null) {
          const [, key, value] = match
          if (key && value !== undefined) {
            dict[key] = value
          }
        }
      }
    }
    
    // Approach 2: If no full dict found, try line-by-line parsing for malformed dicts
    if (Object.keys(dict).length === 0) {
      const lines = text.split('\n')
      for (const line of lines) {
        const lineMatch = line.match(/['"]?([^'":\s]+)['"]?\s*:\s*['"]([^'"]*)['"]?/)
        if (lineMatch) {
          const [, key, value] = lineMatch
          dict[key] = value
        }
      }
    }
    
    return dict
  }

  Object.entries(sectionPatterns).forEach(([key, pattern]) => {
    const matches = htmlContent.match(pattern)
    if (matches) {
      matches.forEach(match => {
        // Look for dictionary structures in the match
        const dictMatches = match.match(/\{[^}]+\}/g)
        if (dictMatches) {
          dictMatches.forEach(dictStr => {
            const parsedDict = parseDictString(dictStr)
            
            if (key === 'decisions' && parsedDict.decision) {
              result.decisions.push({
                decision: parsedDict.decision,
                context: parsedDict.context,
                contexteTemporel: parsedDict.contexteTemporel
              })
            } else if (key === 'technicalDetails' && parsedDict.detail) {
              result.technicalDetails.push({
                detail: parsedDict.detail,
                context: parsedDict.context,
                contexteTemporel: parsedDict.contexteTemporel
              })
            } else if (key === 'risks' && parsedDict.risk) {
              result.risks.push({
                risk: parsedDict.risk,
                context: parsedDict.context,
                contexteTemporel: parsedDict.contexteTemporel
              })
            } else if (key === 'recommendations' && parsedDict.recommendation) {
              result.recommendations.push({
                recommendation: parsedDict.recommendation,
                context: parsedDict.context,
                contexteTemporel: parsedDict.contexteTemporel
              })
            } else if (key === 'keyPoints' && parsedDict.point) {
              result.keyPoints.push({
                point: parsedDict.point,
                context: parsedDict.context,
                contexteTemporel: parsedDict.contexteTemporel
              })
            } else if (key === 'participants' && parsedDict.participant) {
              result.participants.push({
                participant: parsedDict.participant,
                role: parsedDict.role,
                context: parsedDict.context
              })
            }
          })
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
    <div className="space-y-4">
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
            <CardContent className="p-0 overflow-hidden">
              <div className="overflow-x-auto">
                <Table className="w-full table-fixed">
                  <TableHeader>
                    <TableRow className="hover:bg-transparent">
                      <TableHead className="font-bold text-gray-700 w-1/2">Description</TableHead>
                      <TableHead className="font-bold text-gray-700 w-1/3">Contexte</TableHead>
                      <TableHead className="font-bold text-gray-700 w-1/6">
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
                      <TableCell className="font-medium text-gray-800 py-4 min-w-0">
                        <div className="flex items-start gap-2">
                          <div className={`w-2 h-2 rounded-full bg-gradient-to-r ${section.color} mt-2 flex-shrink-0`} />
                          <span className="leading-relaxed break-words whitespace-pre-wrap">{item[section.field]}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-600 py-4 min-w-0 max-w-xs">
                        {item.context && (
                          <div className="text-sm bg-gray-100 p-2 rounded-md italic break-words whitespace-pre-wrap">
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
              </div>
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
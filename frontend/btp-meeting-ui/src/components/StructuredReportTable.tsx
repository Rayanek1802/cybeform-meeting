import React, { useState } from 'react'
import { FileText, Search, AlertCircle, CheckCircle, Clock, Users, Building, Target, Zap, Settings, DollarSign, Shield, ChevronDown, ChevronRight } from 'lucide-react'
import { Badge } from './ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Button } from './ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/table'

interface StructuredReportTableProps {
  reportHtml: string
}

const StructuredReportTable: React.FC<StructuredReportTableProps> = ({ reportHtml }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['problemes', 'actions']))

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId)
    } else {
      newExpanded.add(sectionId)
    }
    setExpandedSections(newExpanded)
  }

  const expandAllSections = () => {
    setExpandedSections(new Set(['problemes', 'actions', 'decisions', 'risques', 'techniques', 'planning', 'financier']))
  }

  const collapseAllSections = () => {
    setExpandedSections(new Set())
  }

  // Parser pour extraire les données du HTML qui contient du contenu Python brut
  const parseReportData = (html: string) => {
    const sections = []

    // Extraire la section "Problemes" avec les dictionnaires Python
    const problemesMatch = html.match(/Problemes\s*\n\s*(.*?)(?=\n\s*[A-Z]|$)/s)
    if (problemesMatch) {
      const problemesText = problemesMatch[1]
      const problemesData = parseProblemesList(problemesText)
      if (problemesData.length > 0) {
        sections.push({
          id: 'problemes',
          title: 'Problèmes Identifiés',
          icon: <AlertCircle className="h-4 w-4" />,
          color: 'red',
          priority: 'high',
          data: problemesData,
          type: 'problems'
        })
      }
    }

    // Ajouter d'autres sections selon les patterns trouvés
    const actionsMatch = html.match(/Actions?\s*\n\s*(.*?)(?=\n\s*[A-Z]|$)/s)
    if (actionsMatch) {
      const actionsData = parseActionsList(actionsMatch[1])
      if (actionsData.length > 0) {
        sections.push({
          id: 'actions',
          title: 'Plan d\'Actions',
          icon: <CheckCircle className="h-4 w-4" />,
          color: 'green',
          priority: 'high',
          data: actionsData,
          type: 'actions'
        })
      }
    }

    const decisionsMatch = html.match(/Decisions?\s*\n\s*(.*?)(?=\n\s*[A-Z]|$)/s)
    if (decisionsMatch) {
      const decisionsData = parseDecisionsList(decisionsMatch[1])
      if (decisionsData.length > 0) {
        sections.push({
          id: 'decisions',
          title: 'Décisions Prises',
          icon: <Target className="h-4 w-4" />,
          color: 'blue',
          priority: 'high',
          data: decisionsData,
          type: 'decisions'
        })
      }
    }

    const risquesMatch = html.match(/Risques?\s*\n\s*(.*?)(?=\n\s*[A-Z]|$)/s)
    if (risquesMatch) {
      const risquesData = parseRisquesList(risquesMatch[1])
      if (risquesData.length > 0) {
        sections.push({
          id: 'risques',
          title: 'Analyse des Risques',
          icon: <Shield className="h-4 w-4" />,
          color: 'orange',
          priority: 'high',
          data: risquesData,
          type: 'risks'
        })
      }
    }

    return sections
  }

  // Parser pour la liste des problèmes
  const parseProblemesList = (text: string) => {
    const problems = []
    // Regex pour capturer les dictionnaires Python
    const dictPattern = /\{[^}]+\}/g
    const matches = text.match(dictPattern)
    
    if (matches) {
      matches.forEach((match, index) => {
        try {
          // Convertir le format Python en objet JavaScript
          const cleaned = match
            .replace(/'/g, '"')
            .replace(/(\w+):/g, '"$1":')
          const parsed = JSON.parse(cleaned)
          
          problems.push({
            id: index + 1,
            description: parsed.description || 'Description non disponible',
            context: parsed.context || parsed.details || 'Contexte non spécifié',
            timeRange: parsed.contexteTemporel || 'Non spécifié',
            severity: determineSeverity(parsed.description)
          })
        } catch (e) {
          // En cas d'erreur de parsing, extraire manuellement
          const description = extractValue(match, 'description')
          const context = extractValue(match, 'context') || extractValue(match, 'details')
          const timeRange = extractValue(match, 'contexteTemporel')
          
          if (description) {
            problems.push({
              id: index + 1,
              description,
              context: context || 'Contexte non spécifié',
              timeRange: timeRange || 'Non spécifié',
              severity: determineSeverity(description)
            })
          }
        }
      })
    }
    
    return problems
  }

  const parseActionsList = (text: string) => {
    // Parser similaire pour les actions
    return []
  }

  const parseDecisionsList = (text: string) => {
    // Parser similaire pour les décisions
    return []
  }

  const parseRisquesList = (text: string) => {
    // Parser similaire pour les risques
    return []
  }

  const extractValue = (dictString: string, key: string) => {
    const regex = new RegExp(`'${key}':\\s*'([^']*)'`)
    const match = dictString.match(regex)
    return match ? match[1] : null
  }

  const determineSeverity = (description: string) => {
    const lowerDesc = description.toLowerCase()
    if (lowerDesc.includes('critique') || lowerDesc.includes('urgent') || lowerDesc.includes('blocage')) {
      return 'critical'
    } else if (lowerDesc.includes('important') || lowerDesc.includes('risque') || lowerDesc.includes('problème')) {
      return 'high'
    } else if (lowerDesc.includes('attention') || lowerDesc.includes('surveillance')) {
      return 'medium'
    }
    return 'low'
  }

  const getSeverityBadge = (severity: string) => {
    const badges = {
      critical: <Badge className="bg-red-100 text-red-800 border-red-300">Critique</Badge>,
      high: <Badge className="bg-orange-100 text-orange-800 border-orange-300">Élevé</Badge>,
      medium: <Badge className="bg-yellow-100 text-yellow-800 border-yellow-300">Moyen</Badge>,
      low: <Badge className="bg-gray-100 text-gray-800 border-gray-300">Faible</Badge>
    }
    return badges[severity as keyof typeof badges] || badges.low
  }

  const getColorClasses = (color: string) => {
    const colors = {
      red: 'bg-red-50 text-red-700 border-red-200',
      green: 'bg-green-50 text-green-700 border-green-200',
      blue: 'bg-blue-50 text-blue-700 border-blue-200',
      orange: 'bg-orange-50 text-orange-700 border-orange-200',
      purple: 'bg-purple-50 text-purple-700 border-purple-200'
    }
    return colors[color as keyof typeof colors] || colors.blue
  }

  const sections = parseReportData(reportHtml)
  
  const filteredSections = sections.filter(section => 
    section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    section.data.some((item: any) => 
      item.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      item.context?.toLowerCase().includes(searchTerm.toLowerCase())
    )
  )

  return (
    <Card className="border-gray-200 shadow-lg">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md">
              <FileText className="h-5 w-5" />
            </div>
            Rapport d'analyse structuré
            <Badge variant="outline" className="bg-purple-50 text-purple-700 border-purple-200 ml-4">
              {sections.length} sections
            </Badge>
          </CardTitle>
          
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <Input
                placeholder="Rechercher dans le rapport..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 w-64 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200"
              />
            </div>
            
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={expandAllSections}
                className="text-xs"
              >
                Tout développer
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={collapseAllSections}
                className="text-xs"
              >
                Tout réduire
              </Button>
            </div>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {filteredSections.map((section) => (
          <div key={section.id} className="border border-gray-200 rounded-lg overflow-hidden shadow-sm">
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full px-6 py-4 bg-gradient-to-r from-gray-50 to-white hover:from-gray-100 hover:to-gray-50 border-b border-gray-200 flex items-center justify-between transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-lg ${getColorClasses(section.color)} border`}>
                  {section.icon}
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">{section.title}</h3>
                  <div className="flex items-center gap-2 mt-1">
                    <Badge variant="outline" className="text-xs">
                      {section.data.length} élément{section.data.length !== 1 ? 's' : ''}
                    </Badge>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {expandedSections.has(section.id) ? (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                )}
              </div>
            </button>
            
            {expandedSections.has(section.id) && (
              <div className="p-0">
                {section.type === 'problems' && (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[60px]">ID</TableHead>
                        <TableHead className="w-[80px]">Gravité</TableHead>
                        <TableHead className="w-[120px]">Période</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Contexte</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {section.data.map((problem: any) => (
                        <TableRow key={problem.id} className="hover:bg-red-50">
                          <TableCell className="font-mono text-sm">
                            #{problem.id.toString().padStart(2, '0')}
                          </TableCell>
                          <TableCell>
                            {getSeverityBadge(problem.severity)}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline" className="font-mono text-xs">
                              {problem.timeRange}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-medium">
                            <div className="max-w-md">
                              {searchTerm ? (
                                <span
                                  dangerouslySetInnerHTML={{
                                    __html: problem.description.replace(
                                      new RegExp(searchTerm, 'gi'),
                                      '<mark class="bg-yellow-200 px-1 rounded">$&</mark>'
                                    )
                                  }}
                                />
                              ) : (
                                problem.description
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-600">
                            <div className="max-w-sm">
                              {searchTerm ? (
                                <span
                                  dangerouslySetInnerHTML={{
                                    __html: problem.context.replace(
                                      new RegExp(searchTerm, 'gi'),
                                      '<mark class="bg-yellow-200 px-1 rounded">$&</mark>'
                                    )
                                  }}
                                />
                              ) : (
                                problem.context
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </div>
            )}
          </div>
        ))}
        
        {filteredSections.length === 0 && searchTerm && (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <Search className="h-12 w-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun résultat trouvé</h3>
            <p className="text-gray-500 text-center max-w-md">
              Aucune section ne correspond à votre recherche "{searchTerm}". 
              Essayez avec d'autres mots-clés.
            </p>
          </div>
        )}
        
        {sections.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 px-6">
            <FileText className="h-12 w-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune donnée structurée trouvée</h3>
            <p className="text-gray-500 text-center max-w-md">
              Le rapport ne contient pas de données structurées parsables. 
              Vérifiez le format des données d'analyse.
            </p>
          </div>
        )}
        
        {/* Footer avec statistiques */}
        <div className="bg-gradient-to-r from-gray-50 to-purple-50 p-4 rounded-lg border border-gray-200 mt-6">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                Rapport analysé et structuré
              </span>
              <span>Sections: {sections.length}</span>
              <span>
                Total éléments: {sections.reduce((acc, section) => acc + section.data.length, 0)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default StructuredReportTable
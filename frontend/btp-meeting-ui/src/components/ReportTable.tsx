import React, { useState } from 'react'
import { FileText, ChevronDown, ChevronRight, Search, AlertCircle, CheckCircle, Clock, Users } from 'lucide-react'
import { Badge } from './ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from './ui/card'
import { Input } from './ui/input'
import { Button } from './ui/button'

interface ReportTableProps {
  reportHtml: string
}

const ReportTable: React.FC<ReportTableProps> = ({ reportHtml }) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['summary']))

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
    setExpandedSections(new Set(['summary', 'actions', 'risks', 'decisions', 'technical', 'planning']))
  }

  const collapseAllSections = () => {
    setExpandedSections(new Set())
  }

  // Parser simple pour extraire les sections du HTML
  const extractSections = (html: string) => {
    const sections = []
    
    // Section résumé
    const summaryMatch = html.match(/<h[23]>.*?(résumé|objectifs?).*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (summaryMatch) {
      sections.push({
        id: 'summary',
        title: 'Résumé & Objectifs',
        content: summaryMatch[2],
        icon: <FileText className="h-4 w-4" />,
        color: 'blue',
        priority: 'high'
      })
    }

    // Actions
    const actionsMatch = html.match(/<h[23]>.*?actions?.*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (actionsMatch) {
      sections.push({
        id: 'actions',
        title: 'Actions & Tâches',
        content: actionsMatch[2],
        icon: <CheckCircle className="h-4 w-4" />,
        color: 'green',
        priority: 'high'
      })
    }

    // Risques
    const risksMatch = html.match(/<h[23]>.*?risques?.*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (risksMatch) {
      sections.push({
        id: 'risks',
        title: 'Risques & Mitigations',
        content: risksMatch[2],
        icon: <AlertCircle className="h-4 w-4" />,
        color: 'red',
        priority: 'high'
      })
    }

    // Décisions
    const decisionsMatch = html.match(/<h[23]>.*?décisions?.*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (decisionsMatch) {
      sections.push({
        id: 'decisions',
        title: 'Décisions Prises',
        content: decisionsMatch[2],
        icon: <CheckCircle className="h-4 w-4" />,
        color: 'purple',
        priority: 'medium'
      })
    }

    // Aspects techniques
    const technicalMatch = html.match(/<h[23]>.*?(technique|technical).*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (technicalMatch) {
      sections.push({
        id: 'technical',
        title: 'Aspects Techniques',
        content: technicalMatch[2],
        icon: <Users className="h-4 w-4" />,
        color: 'indigo',
        priority: 'medium'
      })
    }

    // Planning
    const planningMatch = html.match(/<h[23]>.*?(planning|délais?).*?<\/h[23]>(.*?)(?=<h[23]|$)/is)
    if (planningMatch) {
      sections.push({
        id: 'planning',
        title: 'Planning & Délais',
        content: planningMatch[2],
        icon: <Clock className="h-4 w-4" />,
        color: 'orange',
        priority: 'medium'
      })
    }

    // Si aucune section n'est trouvée, retourner le HTML complet
    if (sections.length === 0) {
      sections.push({
        id: 'full',
        title: 'Rapport Complet',
        content: html,
        icon: <FileText className="h-4 w-4" />,
        color: 'gray',
        priority: 'high'
      })
    }

    return sections
  }

  const sections = extractSections(reportHtml)

  const getColorClasses = (color: string) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-700 border-blue-200',
      green: 'bg-green-50 text-green-700 border-green-200', 
      red: 'bg-red-50 text-red-700 border-red-200',
      purple: 'bg-purple-50 text-purple-700 border-purple-200',
      indigo: 'bg-indigo-50 text-indigo-700 border-indigo-200',
      orange: 'bg-orange-50 text-orange-700 border-orange-200',
      gray: 'bg-gray-50 text-gray-700 border-gray-200'
    }
    return colors[color as keyof typeof colors] || colors.gray
  }

  const getPriorityBadge = (priority: string) => {
    const badges = {
      high: <Badge className="bg-red-100 text-red-800 border-red-200 text-xs">Priorité élevée</Badge>,
      medium: <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200 text-xs">Priorité moyenne</Badge>,
      low: <Badge className="bg-gray-100 text-gray-800 border-gray-200 text-xs">Priorité faible</Badge>
    }
    return badges[priority as keyof typeof badges] || badges.low
  }

  const filteredSections = sections.filter(section => 
    section.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    section.content.toLowerCase().includes(searchTerm.toLowerCase())
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
                    {getPriorityBadge(section.priority)}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {section.content.length > 500 ? 'Détaillé' : 'Résumé'}
                </Badge>
                {expandedSections.has(section.id) ? (
                  <ChevronDown className="h-4 w-4 text-gray-400" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-gray-400" />
                )}
              </div>
            </button>
            
            {expandedSections.has(section.id) && (
              <div className="p-6 bg-white">
                <div 
                  className={`prose prose-sm max-w-none ${
                    searchTerm ? 'search-highlight' : ''
                  }`}
                  dangerouslySetInnerHTML={{
                    __html: searchTerm 
                      ? section.content.replace(
                          new RegExp(searchTerm, 'gi'),
                          '<mark class="bg-yellow-200 px-1 rounded">$&</mark>'
                        )
                      : section.content
                  }}
                />
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
        
        {/* Footer avec statistiques */}
        <div className="bg-gradient-to-r from-gray-50 to-purple-50 p-4 rounded-lg border border-gray-200">
          <div className="flex items-center justify-between text-xs text-gray-600">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-purple-500"></div>
                Rapport analysé et structuré
              </span>
              <span>Sections: {sections.length}</span>
            </div>
            <div className="flex items-center gap-2">
              <span>Longueur totale: ~{Math.round(reportHtml.length / 1000)}k caractères</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default ReportTable
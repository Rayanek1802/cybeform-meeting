import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, FolderOpen, Calendar, Users, Building2, CheckCircle, Clock, AlertCircle, MoreVertical, Edit3, Trash2 } from 'lucide-react'
import { motion } from 'framer-motion'

import { Button } from '../components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../components/ui/dialog'
import { Input } from '../components/ui/input'
import { Label } from '../components/ui/label'
import { Badge } from '../components/ui/badge'
import { useToast } from '../components/ui/toaster'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu'

import { projectsApi, type Project } from '../lib/api.ts'
import { useProjectActions, useUIActions } from '../store/useStore'
import { formatDate } from '../lib/utils'
import Layout from '../components/Layout'
import EditProjectDialog from '../components/EditProjectDialog'
import DeleteProjectDialog from '../components/DeleteProjectDialog'

const HomePage: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [projectName, setProjectName] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  
  // Dialog states for edit/delete
  const [editDialog, setEditDialog] = useState<{ open: boolean; project: Project | null }>({
    open: false,
    project: null
  })
  const [deleteDialog, setDeleteDialog] = useState<{ open: boolean; project: Project | null }>({
    open: false,
    project: null
  })
  const [isSaving, setIsSaving] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  const { addProject } = useProjectActions()
  const { setError } = useUIActions()
  const { addToast } = useToast()

  // Load projects on mount
  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const data = await projectsApi.list()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
      setError('Erreur lors du chargement des projets')
      addToast({
        title: 'Erreur',
        description: 'Impossible de charger les projets',
        variant: 'error'
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateProject = async () => {
    if (!projectName.trim()) return

    try {
      setIsCreating(true)
      const newProject = await projectsApi.create({ name: projectName.trim() })
      
      setProjects(prev => [newProject, ...prev])
      addProject(newProject)
      
      addToast({
        title: 'Succès',
        description: 'Projet créé avec succès',
        variant: 'success'
      })
      
      setShowCreateDialog(false)
      setProjectName('')
      
    } catch (error) {
      console.error('Failed to create project:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de créer le projet',
        variant: 'error'
      })
    } finally {
      setIsCreating(false)
    }
  }

  const handleEditProject = (project: Project) => {
    setEditDialog({ open: true, project })
  }

  const handleDeleteProject = (project: Project) => {
    setDeleteDialog({ open: true, project })
  }

  const handleSaveEdit = async (data: { name: string }) => {
    if (!editDialog.project) return

    try {
      setIsSaving(true)
      const updatedProject = await projectsApi.update(editDialog.project.id, data)
      
      // Update projects list
      setProjects(prev => 
        prev.map(p => p.id === editDialog.project!.id ? updatedProject : p)
      )
      
      addToast({
        title: 'Succès',
        description: 'Projet modifié avec succès',
        variant: 'success'
      })
      
      setEditDialog({ open: false, project: null })
    } catch (error) {
      console.error('Failed to update project:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de modifier le projet',
        variant: 'error'
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleConfirmDelete = async () => {
    if (!deleteDialog.project) return

    try {
      setIsDeleting(true)
      await projectsApi.delete(deleteDialog.project.id)
      
      // Remove from projects list
      setProjects(prev => prev.filter(p => p.id !== deleteDialog.project!.id))
      
      addToast({
        title: 'Succès',
        description: 'Projet supprimé avec succès',
        variant: 'success'
      })
      
      setDeleteDialog({ open: false, project: null })
    } catch (error) {
      console.error('Failed to delete project:', error)
      addToast({
        title: 'Erreur',
        description: 'Impossible de supprimer le projet',
        variant: 'error'
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header Section */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Mes projets BTP</h1>
            <p className="text-gray-600 mt-1">
              {projects.length} projet{projects.length > 1 ? 's' : ''} enregistré{projects.length > 1 ? 's' : ''}
            </p>
          </div>
          <Button 
            onClick={() => setShowCreateDialog(true)} 
            className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 rounded-xl"
          >
            <Plus className="h-4 w-4" />
            Nouveau projet
          </Button>
        </div>

        {/* Welcome State */}
        {projects.length === 0 && !isLoading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center py-20"
          >
            <div className="max-w-md mx-auto">
              <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6">
                <FolderOpen className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Aucun projet créé
              </h3>
              <p className="text-gray-600 mb-8">
                Commencez par créer votre premier projet BTP pour organiser et analyser vos réunions de chantier.
              </p>
              <Button 
                onClick={() => setShowCreateDialog(true)} 
                size="lg" 
                className="gap-2 bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 hover:-translate-y-0.5 rounded-xl"
              >
                <Plus className="h-4 w-4" />
                Créer mon premier projet
              </Button>
            </div>
          </motion.div>
        )}

        {/* Projects Grid */}
        {projects.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
            {projects.map((project, index) => (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="hover:shadow-lg transition-shadow duration-200 border-gray-200">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                          <Building2 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900">{project.name}</h3>
                          <p className="text-sm text-gray-500">
                            Créé le {formatDate(project.created_at)}
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
                          <DropdownMenuItem onClick={() => handleEditProject(project)}>
                            <Edit3 className="mr-2 h-4 w-4" />
                            Modifier le nom
                          </DropdownMenuItem>
                          
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => handleDeleteProject(project)}
                            className="text-red-600 focus:text-red-600"
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Supprimer
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-4 h-4" />
                        <span>0 meeting</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Users className="w-4 h-4" />
                        <span>0 participant</span>
                      </div>
                    </div>

                    <Link to={`/projects/${project.id}`}>
                      <Button variant="outline" className="w-full">
                        <FolderOpen className="w-4 h-4 mr-2" />
                        Ouvrir le projet
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-20">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
              <span className="text-gray-600">Chargement des projets...</span>
            </div>
          </div>
        )}
      </div>

      {/* Create Project Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Créer un nouveau projet BTP</DialogTitle>
            <DialogDescription>
              Donnez un nom à votre projet pour commencer à organiser vos réunions de chantier.
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
                    handleCreateProject()
                  }
                }}
              />
            </div>
          </div>
          
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => setShowCreateDialog(false)}
              disabled={isCreating}
            >
              Annuler
            </Button>
            <Button
              onClick={handleCreateProject}
              disabled={!projectName.trim() || isCreating}
              className="bg-gradient-to-r from-[#4F46E5] to-[#C026D3] hover:from-[#4338CA] hover:to-[#A21CAF] text-white border-none shadow-lg hover:shadow-xl transition-all duration-200 disabled:opacity-50 disabled:pointer-events-none rounded-xl"
            >
              {isCreating ? 'Création...' : 'Créer le projet'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Project Dialog */}
      <EditProjectDialog
        project={editDialog.project}
        open={editDialog.open}
        onClose={() => setEditDialog({ open: false, project: null })}
        onSave={handleSaveEdit}
        isSaving={isSaving}
      />

      {/* Delete Project Dialog */}
      <DeleteProjectDialog
        project={deleteDialog.project}
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, project: null })}
        onConfirm={handleConfirmDelete}
        isDeleting={isDeleting}
      />
    </Layout>
  )
}

export default HomePage
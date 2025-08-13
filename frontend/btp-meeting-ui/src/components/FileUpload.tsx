import React, { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, File, AlertCircle, CheckCircle, X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { formatFileSize, isValidAudioFile } from '../lib/utils'

interface FileUploadProps {
  onFileSelect: (file: File) => void
  onUploadProgress?: (progress: number) => void
  onUploadComplete?: () => void
  onUploadError?: (error: string) => void
  disabled?: boolean
  maxSizeMB?: number
}

const FileUpload: React.FC<FileUploadProps> = ({
  onFileSelect,
  onUploadProgress,
  onUploadComplete,
  onUploadError,
  disabled = false,
  maxSizeMB = 500
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    console.log('onDrop called:', { acceptedFiles, rejectedFiles })
    setError(null)
    setSuccess(false)
    
    if (rejectedFiles.length > 0) {
      console.log('Files rejected:', rejectedFiles)
      const rejection = rejectedFiles[0]
      if (rejection.errors.some((e: any) => e.code === 'file-too-large')) {
        setError(`Fichier trop volumineux. Taille maximum: ${maxSizeMB}MB`)
      } else if (rejection.errors.some((e: any) => e.code === 'file-invalid-type')) {
        setError('Format de fichier non supporté. Utilisez MP3, WAV, M4A ou WEBM.')
      } else {
        setError('Erreur lors de la sélection du fichier.')
      }
      return
    }

    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0]
      console.log('File accepted:', { name: file.name, type: file.type, size: file.size })
      
      // Additional validation
      if (!isValidAudioFile(file)) {
        console.log('File validation failed for:', file.type)
        setError('Format de fichier non supporté. Utilisez MP3, WAV, M4A ou WEBM.')
        return
      }

      console.log('File validated successfully, calling onFileSelect')
      setSelectedFile(file)
      onFileSelect(file)
      setSuccess(true)
    }
  }, [onFileSelect, maxSizeMB])

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'audio/*': ['.mp3', '.wav', '.m4a', '.webm', '.opus', '.aac', '.ogg', '.flac']
    },
    maxFiles: 1,
    maxSize: maxSizeMB * 1024 * 1024,
    disabled: disabled || isUploading,
    // More permissive validation - let our custom validation handle type checking
    validator: null
  })

  const clearFile = () => {
    setSelectedFile(null)
    setError(null)
    setSuccess(false)
    setUploadProgress(0)
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <Card
        {...getRootProps()}
        className={`
          cursor-pointer transition-all duration-200 border-2 border-dashed
          ${isDragActive && !isDragReject
            ? 'border-brand-primary bg-brand-primary/5'
            : isDragReject
            ? 'border-red-500 bg-red-50'
            : 'border-border hover:border-brand-primary/50 hover:bg-muted/50'
          }
          ${disabled || isUploading ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <CardContent className="p-8 text-center">
          <input {...getInputProps()} />
          
          <div className="space-y-4">
            <div className="flex justify-center">
              <div className={`
                h-16 w-16 rounded-full flex items-center justify-center
                ${isDragActive && !isDragReject
                  ? 'bg-brand-primary/10'
                  : 'bg-muted'
                }
              `}>
                <Upload className={`
                  h-8 w-8
                  ${isDragActive && !isDragReject
                    ? 'text-brand-primary'
                    : 'text-muted-foreground'
                  }
                `} />
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-2">
                {isDragActive
                  ? isDragReject
                    ? 'Fichier non supporté'
                    : 'Relâchez pour uploader'
                  : 'Glissez-déposez votre fichier audio'
                }
              </h3>
              
              {!isDragActive && (
                <div className="space-y-2">
                  <p className="text-muted-foreground">
                    ou <span className="text-brand-primary font-medium">cliquez pour parcourir</span>
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Formats supportés: MP3, WAV, M4A, WEBM • Max {maxSizeMB}MB
                  </p>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Selected File Info */}
      {selectedFile && (
        <Card className={`transition-all duration-200 ${success ? 'border-green-200 bg-green-50' : ''}`}>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-brand-primary/10 flex items-center justify-center">
                  <File className="h-5 w-5 text-brand-primary" />
                </div>
                <div>
                  <p className="font-medium">{selectedFile.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {formatFileSize(selectedFile.size)}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                {success && (
                  <CheckCircle className="h-5 w-5 text-green-600" />
                )}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={clearFile}
                  disabled={isUploading}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            {/* Upload Progress */}
            {isUploading && (
              <div className="mt-3">
                <Progress value={uploadProgress} showLabel />
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Error Message */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-700">
              <AlertCircle className="h-5 w-5" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Success Message */}
      {success && selectedFile && !error && (
        <Card className="border-green-200 bg-green-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-green-700">
              <CheckCircle className="h-5 w-5" />
              <p className="text-sm font-medium">
                Fichier sélectionné avec succès • Prêt pour l'analyse
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default FileUpload

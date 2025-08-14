import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date)
  } catch (error) {
    return 'Date invalide'
  }
}

export function formatDuration(seconds: number): string {
  if (!seconds || seconds <= 0) return '0 min'
  
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  
  if (minutes === 0) {
    return `${remainingSeconds}s`
  } else if (remainingSeconds === 0) {
    return `${minutes}m`
  } else {
    return `${minutes}m ${remainingSeconds}s`
  }
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function isValidAudioFile(file: File): boolean {
  const validTypes = [
    'audio/mp3',
    'audio/mpeg',
    'audio/wav',
    'audio/wave',
    'audio/x-wav',
    'audio/aac',
    'audio/ogg',
    'audio/webm',
    'audio/flac',
    'audio/x-flac',
    'audio/mp4',
    'audio/m4a',
    'audio/x-m4a',
    'audio/mp4a-latm',
    // Fallback: check by file extension if MIME type is unknown
    ''
  ]
  
  // First check MIME type
  if (file.type && validTypes.includes(file.type.toLowerCase())) {
    return true
  }
  
  // Fallback: check file extension
  const fileName = file.name.toLowerCase()
  const validExtensions = ['.mp3', '.wav', '.m4a', '.webm', '.ogg', '.flac', '.aac']
  
  return validExtensions.some(ext => fileName.endsWith(ext))
}

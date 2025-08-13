import { useState, useRef, useCallback } from 'react'

export interface AudioRecorderState {
  isRecording: boolean
  isPaused: boolean
  duration: number
  audioBlob: Blob | null
  audioUrl: string | null
  error: string | null
}

export interface AudioRecorderControls {
  startRecording: () => Promise<void>
  pauseRecording: () => void
  resumeRecording: () => void
  stopRecording: () => void
  resetRecording: () => void
}

export const useAudioRecorder = (): AudioRecorderState & AudioRecorderControls => {
  const [isRecording, setIsRecording] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [duration, setDuration] = useState(0)
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const startTimeRef = useRef<number>(0)
  const pausedTimeRef = useRef<number>(0)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const updateDuration = useCallback(() => {
    if (startTimeRef.current && !isPaused) {
      const elapsed = (Date.now() - startTimeRef.current - pausedTimeRef.current) / 1000
      setDuration(Math.floor(elapsed))
    }
  }, [isPaused])

  const startRecording = useCallback(async () => {
    try {
      setError(null)
      
      // Get user media
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        }
      })

      streamRef.current = stream

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      mediaRecorderRef.current = mediaRecorder
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' })
        setAudioBlob(blob)
        setAudioUrl(URL.createObjectURL(blob))
        
        // Cleanup
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop())
          streamRef.current = null
        }
      }

      // Start recording
      mediaRecorder.start(100) // Collect data every 100ms
      setIsRecording(true)
      setIsPaused(false)
      startTimeRef.current = Date.now()
      pausedTimeRef.current = 0

      // Start duration timer
      intervalRef.current = setInterval(updateDuration, 1000)

    } catch (err) {
      console.error('Error starting recording:', err)
      setError('Impossible d\'accéder au microphone. Vérifiez les permissions.')
    }
  }, [updateDuration])

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && !isPaused) {
      mediaRecorderRef.current.pause()
      setIsPaused(true)
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isRecording, isPaused])

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording && isPaused) {
      const pauseStart = Date.now()
      mediaRecorderRef.current.resume()
      setIsPaused(false)
      
      // Update paused time
      pausedTimeRef.current += Date.now() - pauseStart
      
      // Restart timer
      intervalRef.current = setInterval(updateDuration, 1000)
    }
  }, [isRecording, isPaused, updateDuration])

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      setIsPaused(false)
      
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [isRecording])

  const resetRecording = useCallback(() => {
    // Stop any ongoing recording
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
    }

    // Stop any streams
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }

    // Clear interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }

    // Revoke audio URL
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl)
    }

    // Reset state
    setIsRecording(false)
    setIsPaused(false)
    setDuration(0)
    setAudioBlob(null)
    setAudioUrl(null)
    setError(null)
    
    mediaRecorderRef.current = null
    chunksRef.current = []
    startTimeRef.current = 0
    pausedTimeRef.current = 0
  }, [isRecording, audioUrl])

  return {
    // State
    isRecording,
    isPaused,
    duration,
    audioBlob,
    audioUrl,
    error,
    
    // Controls
    startRecording,
    pauseRecording,
    resumeRecording,
    stopRecording,
    resetRecording,
  }
}

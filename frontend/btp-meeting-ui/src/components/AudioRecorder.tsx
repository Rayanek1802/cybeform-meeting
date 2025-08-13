import React from 'react'
import { Mic, Square, Play, Pause, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useAudioRecorder } from '@/hooks/useAudioRecorder'
import { formatDuration } from '@/lib/utils'

interface AudioRecorderProps {
  onRecordingComplete: (audioBlob: Blob, duration: number) => void
  disabled?: boolean
}

const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
  disabled = false
}) => {
  const {
    isRecording,
    isPaused,
    duration,
    audioBlob,
    audioUrl,
    error,
    startRecording,
    pauseRecording,
    resumeRecording,
    stopRecording,
    resetRecording,
  } = useAudioRecorder()

  const handleStop = () => {
    stopRecording()
    if (audioBlob) {
      onRecordingComplete(audioBlob, duration)
    }
  }

  const handleReset = () => {
    resetRecording()
  }

  React.useEffect(() => {
    if (audioBlob && duration > 0) {
      onRecordingComplete(audioBlob, duration)
    }
  }, [audioBlob, duration, onRecordingComplete])

  return (
    <Card className="w-full">
      <CardContent className="p-6">
        <div className="space-y-4">
          {/* Status */}
          <div className="text-center">
            <div className="flex items-center justify-center gap-2 mb-2">
              <div
                className={`h-3 w-3 rounded-full ${
                  isRecording && !isPaused
                    ? 'bg-red-500 animate-pulse'
                    : isPaused
                    ? 'bg-yellow-500'
                    : 'bg-gray-300'
                }`}
              />
              <span className="text-sm font-medium">
                {isRecording && !isPaused
                  ? 'Enregistrement en cours'
                  : isPaused
                  ? 'Enregistrement en pause'
                  : 'Prêt à enregistrer'}
              </span>
            </div>
            
            <div className="text-2xl font-mono font-bold text-brand-primary">
              {formatDuration(duration)}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          {/* Controls */}
          <div className="flex justify-center gap-3">
            {!isRecording ? (
              <Button
                onClick={startRecording}
                disabled={disabled}
                size="lg"
                className="gap-2"
              >
                <Mic className="h-5 w-5" />
                Commencer l'enregistrement
              </Button>
            ) : (
              <>
                {isPaused ? (
                  <Button
                    onClick={resumeRecording}
                    size="lg"
                    variant="success"
                    className="gap-2"
                  >
                    <Play className="h-5 w-5" />
                    Reprendre
                  </Button>
                ) : (
                  <Button
                    onClick={pauseRecording}
                    size="lg"
                    variant="warning"
                    className="gap-2"
                  >
                    <Pause className="h-5 w-5" />
                    Pause
                  </Button>
                )}
                
                <Button
                  onClick={handleStop}
                  size="lg"
                  variant="destructive"
                  className="gap-2"
                >
                  <Square className="h-5 w-5" />
                  Arrêter
                </Button>
                
                <Button
                  onClick={handleReset}
                  size="lg"
                  variant="outline"
                  className="gap-2"
                >
                  <RotateCcw className="h-5 w-5" />
                  Reset
                </Button>
              </>
            )}
          </div>

          {/* Audio Preview */}
          {audioUrl && !isRecording && (
            <div className="space-y-3">
              <div className="text-center">
                <p className="text-sm text-muted-foreground mb-2">
                  Aperçu de l'enregistrement
                </p>
                <audio controls className="w-full max-w-md mx-auto">
                  <source src={audioUrl} type="audio/webm" />
                  Votre navigateur ne supporte pas la lecture audio.
                </audio>
              </div>
              
              <div className="flex justify-center gap-2">
                <Button
                  onClick={handleReset}
                  variant="outline"
                  size="sm"
                  className="gap-2"
                >
                  <RotateCcw className="h-4 w-4" />
                  Refaire
                </Button>
              </div>
            </div>
          )}

          {/* Tips */}
          {!isRecording && !audioBlob && (
            <div className="text-center text-sm text-muted-foreground">
              <p>
                🎙️ Assurez-vous d'être dans un environnement silencieux pour une meilleure qualité d'enregistrement.
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default AudioRecorder

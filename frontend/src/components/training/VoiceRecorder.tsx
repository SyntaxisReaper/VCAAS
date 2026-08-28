'use client'

import { useState, useCallback, useRef } from 'react'
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/outline'

interface VoiceRecorderProps {
  onRecordingComplete: (audioFile: File, duration: number) => void
  isDisabled?: boolean
}

export default function VoiceRecorder({ onRecordingComplete, isDisabled = false }: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const recordingIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 44100,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      })
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })
      
      const chunks: BlobPart[] = []
      
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data)
      }
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' })
        const file = new File([blob], `recording-${Date.now()}.webm`, {
          type: 'audio/webm'
        })
        
        onRecordingComplete(file, recordingTime)
        stream.getTracks().forEach(track => track.stop())
      }
      
      mediaRecorderRef.current = mediaRecorder
      mediaRecorder.start()
      setIsRecording(true)
      setRecordingTime(0)
      
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
    } catch (error) {
      console.error('Error starting recording:', error)
      alert('Unable to access microphone. Please check permissions.')
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current)
      }
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="border-2 border-gray-200 rounded-lg p-4 bg-white">
      <h3 className="text-md font-medium text-gray-900 mb-3 flex items-center">
        <MicrophoneIcon className="h-5 w-5 mr-2 text-primary-600" />
        Record New Sample
      </h3>
      <div className="flex items-center space-x-4">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          disabled={isDisabled}
          className={`w-16 h-16 rounded-full flex items-center justify-center transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
            isRecording 
              ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
              : 'bg-primary-600 hover:bg-primary-700'
          }`}
        >
          {isRecording ? (
            <StopIcon className="h-6 w-6 text-white" />
          ) : (
            <MicrophoneIcon className="h-6 w-6 text-white" />
          )}
        </button>
        <div>
          <p className="text-sm text-gray-600">
            {isRecording ? `Recording... ${formatTime(recordingTime)}` : 'Click to start recording'}
          </p>
          <p className="text-xs text-gray-500">
            Speak clearly for at least 1 minute
          </p>
        </div>
      </div>
    </div>
  )
}

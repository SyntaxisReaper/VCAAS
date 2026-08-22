'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { useDropzone } from 'react-dropzone'
import { motion } from 'framer-motion'
import { UploadCloud, FileText, Trash2, ArrowLeft, Upload, Activity } from 'lucide-react'
import axios from 'axios'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

type AudioFile = {
  id: string
  name: string
  size: number
  duration: number
  file: File
  preview?: string
}

export default function VoiceTrainingPage() {
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [spectralOk, setSpectralOk] = useState<boolean | null>(null)
  const [voiceName, setVoiceName] = useState('')

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles = acceptedFiles.map((file, index) => ({
      id: `file-${Date.now()}-${index}`,
      name: file.name,
      size: file.size,
      duration: 0,
      file,
      preview: URL.createObjectURL(file)
    }))
    setAudioFiles(prev => [...prev, ...newFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg'] },
    maxFiles: 10,
    maxSize: 100 * 1024 * 1024
  })

  const removeFile = (id: string) => setAudioFiles(prev => prev.filter(f => f.id !== id))

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const handleAnalyze = async () => {
    if (audioFiles.length === 0) return alert('Upload at least one audio file')
    try {
      setIsUploading(true)
      const fd = new FormData()
      fd.append('file', audioFiles[0].file)
      const res = await axios.post(`${API}/api/v1/verify/spectral-graphs`, fd, { headers: { 'Content-Type': 'multipart/form-data' } })
      setSpectralOk(!!res.data?.mel_db)
    } catch (e) {
      setSpectralOk(false)
    } finally {
      setIsUploading(false)
    }
  }

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-8 flex items-center space-x-4">
          <Link href="/dashboard" className="p-2 border border-[var(--border)] bg-[var(--surface)] hover:bg-white/10 rounded-lg transition-colors text-[var(--text-1)]">
            <ArrowLeft className="h-5 w-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-[var(--text-1)] tracking-tight mb-1">Create New Voice</h1>
            <p className="text-[var(--text-2)]">Upload audio samples to analyze spectral features and train a new clone</p>
          </div>
        </motion.div>

        <div className="max-w-3xl mx-auto px-4 sm:px-0 py-8">
          <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5, delay: 0.1 }} className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-8">
            <h2 className="text-xl font-semibold text-[var(--text-1)] mb-6 flex items-center space-x-2">
              <Upload className="w-5 h-5 text-[var(--text-2)]" />
              <span>Upload Voice Samples</span>
            </h2>
            
            <div {...getRootProps()} className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${isDragActive ? 'border-white bg-white/5' : 'border-[var(--border)] bg-black hover:border-white/30 hover:bg-white/5'}`}>
              <input {...getInputProps()} />
              <div className="w-16 h-16 mx-auto mb-4 bg-white/10 border border-white/10 rounded-full flex items-center justify-center">
                <UploadCloud className="w-8 h-8 text-[var(--text-1)]" />
              </div>
              <p className="text-lg font-semibold text-[var(--text-1)] mb-2">{isDragActive ? 'Drop files here' : 'Select Audio Files'}</p>
              <p className="text-[var(--text-2)] text-sm">Drag and drop your audio files, or click to browse</p>
              <p className="text-[var(--text-2)]/50 text-xs mt-4">Supported: .wav, .mp3, .m4a, .flac (Max 100MB)</p>
            </div>

            {audioFiles.length > 0 && (
              <div className="mt-8 space-y-3">
                <h3 className="text-sm font-medium text-[var(--text-2)] mb-3">Selected Files ({audioFiles.length})</h3>
                {audioFiles.map((file) => (
                  <div key={file.id} className="flex items-center justify-between p-4 bg-black border border-[var(--border)] rounded-lg group hover:border-white/20 transition-colors">
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-white/5 border border-white/10 rounded flex items-center justify-center">
                        <FileText className="w-5 h-5 text-[var(--text-1)]" />
                      </div>
                      <div>
                        <p className="font-medium text-[var(--text-1)] text-sm">{file.name}</p>
                        <p className="text-xs text-[var(--text-2)] mt-0.5">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <button onClick={() => removeFile(file.id)} className="p-2 text-[var(--text-2)] hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-8 border-t border-[var(--border)] pt-8">
              <h3 className="text-sm font-medium text-[var(--text-2)] mb-4">Voice Configuration</h3>
              <div className="flex flex-col sm:flex-row items-center gap-4">
                <input 
                  value={voiceName} 
                  onChange={(e) => setVoiceName(e.target.value)} 
                  placeholder="Enter a name for this voice..." 
                  className="w-full sm:flex-1 bg-black border border-[var(--border)] text-[var(--text-1)] px-4 py-3 rounded-lg focus:outline-none focus:border-white/30 focus:ring-1 focus:ring-white/30 transition-all placeholder:text-[var(--text-2)]/50" 
                />
                <button 
                  onClick={handleAnalyze} 
                  disabled={audioFiles.length === 0 || isUploading || !voiceName.trim()} 
                  className="w-full sm:w-auto bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2 transition-colors whitespace-nowrap"
                >
                  {isUploading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <Activity className="w-4 h-4" />
                      <span>Analyze Spectral Features</span>
                    </>
                  )}
                </button>
              </div>

              {spectralOk !== null && (
                <div className={`mt-6 p-4 rounded-lg border flex items-start space-x-3 ${spectralOk ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                  <div className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${spectralOk ? 'bg-emerald-400' : 'bg-red-400'}`} />
                  <div>
                    <p className={`text-sm font-medium ${spectralOk ? 'text-emerald-400' : 'text-red-400'}`}>
                      {spectralOk ? 'Analysis Complete' : 'Analysis Failed'}
                    </p>
                    <p className={`text-xs mt-1 ${spectralOk ? 'text-emerald-400/80' : 'text-red-400/80'}`}>
                      {spectralOk ? 'Spectral features successfully extracted and verified by the backend. Ready for training.' : 'Could not extract valid spectral features. Please ensure the audio file is clear and formatted correctly.'}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

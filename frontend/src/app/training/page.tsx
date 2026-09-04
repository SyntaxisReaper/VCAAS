'use client'

import { useState, useCallback } from 'react'
import Link from 'next/link'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import {
  UploadCloud,
  FileText,
  Trash2,
  ArrowLeft,
  Activity,
  CheckCircle2,
  XCircle,
  Mic,
  ChevronRight,
  Info,
} from 'lucide-react'
import axios from 'axios'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] } },
}
const stagger = { visible: { transition: { staggerChildren: 0.08 } } }

type AudioFile = {
  id: string
  name: string
  size: number
  file: File
  preview?: string
}

const TIPS = [
  'Use a quiet, echo-free environment for best results.',
  'Minimum 30 seconds of clean speech per sample.',
  'Avoid music or background noise in your clips.',
  'More varied speech samples produce better clones.',
]

export default function VoiceTrainingPage() {
  const [audioFiles, setAudioFiles] = useState<AudioFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [voiceName, setVoiceName] = useState('')
  const [spectralOk, setSpectralOk] = useState<boolean | null>(null)
  const [spectralData, setSpectralData] = useState<any>(null)

  const onDrop = useCallback((accepted: File[]) => {
    const newFiles = accepted.map((file, i) => ({
      id: `file-${Date.now()}-${i}`,
      name: file.name,
      size: file.size,
      file,
      preview: URL.createObjectURL(file),
    }))
    setAudioFiles(prev => [...prev, ...newFiles])
    setSpectralOk(null)
    setSpectralData(null)
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'audio/*': ['.wav', '.mp3', '.m4a', '.flac', '.ogg'] },
    maxFiles: 10,
    maxSize: 100 * 1024 * 1024,
  })

  const removeFile = (id: string) => {
    setAudioFiles(prev => prev.filter(f => f.id !== id))
    setSpectralOk(null)
  }

  const fmt = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const s = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${s[i]}`
  }

  const handleAnalyze = async () => {
    if (audioFiles.length === 0) return
    setIsUploading(true)
    setSpectralOk(null)
    setSpectralData(null)
    try {
      const fd = new FormData()
      fd.append('file', audioFiles[0].file)
      const res = await axios.post(`${API}/api/v1/verify/spectral-graphs`, fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      const ok = !!res.data?.mel_db
      setSpectralOk(ok)
      setSpectralData(res.data)
    } catch {
      setSpectralOk(false)
    } finally {
      setIsUploading(false)
    }
  }

  const canAnalyze = audioFiles.length > 0 && voiceName.trim().length > 0 && !isUploading

  return (
    <div className="min-h-screen pt-20 pb-16 px-4 sm:px-6 lg:px-8 bg-[var(--bg)]">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial="hidden"
          animate="visible"
          variants={stagger}
          className="mb-10 flex items-start gap-4"
        >
          <motion.div variants={fadeUp}>
            <Link
              href="/dashboard"
              className="mt-1 p-2 border border-[var(--border)] bg-[var(--surface-1)] hover:bg-[var(--surface-2)] rounded-xl transition-colors text-[var(--text-1)] inline-flex"
            >
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </motion.div>
          <motion.div variants={fadeUp}>
            <h1 className="text-3xl font-bold tracking-tight mb-1">Create New Voice</h1>
            <p className="text-[var(--text-2)] text-sm">
              Upload audio samples to analyze spectral features and train a new voice clone.
            </p>
          </motion.div>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Upload Card */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeUp}
            className="lg:col-span-2 bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl p-8"
          >
            <h2 className="text-lg font-semibold mb-6 flex items-center gap-2">
              <Mic className="w-5 h-5 text-[var(--text-2)]" />
              Upload Voice Samples
            </h2>

            {/* Drop zone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all duration-200 ${
                isDragActive
                  ? 'border-[var(--accent)] bg-[var(--accent-bg)]'
                  : 'border-[var(--border)] hover:border-[var(--border-strong)] hover:bg-[var(--surface-2)]'
              }`}
            >
              <input {...getInputProps()} />
              <motion.div
                animate={isDragActive ? { scale: 1.05 } : { scale: 1 }}
                className="w-16 h-16 mx-auto mb-4 bg-[var(--surface-2)] border border-[var(--border)] rounded-2xl flex items-center justify-center"
              >
                <UploadCloud className={`w-8 h-8 transition-colors ${isDragActive ? 'text-[var(--accent)]' : 'text-[var(--text-2)]'}`} />
              </motion.div>
              <p className="text-base font-semibold mb-1">{isDragActive ? 'Drop your files here' : 'Select Audio Files'}</p>
              <p className="text-[var(--text-2)] text-sm">Drag and drop, or click to browse</p>
              <p className="text-[var(--text-3)] text-xs mt-3">.wav · .mp3 · .m4a · .flac · .ogg — Max 100MB each</p>
            </div>

            {/* File list */}
            <AnimatePresence>
              {audioFiles.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className="mt-6 space-y-3"
                >
                  <h3 className="text-sm font-medium text-[var(--text-2)]">Selected ({audioFiles.length})</h3>
                  {audioFiles.map(file => (
                    <motion.div
                      key={file.id}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 8 }}
                      className="flex items-center justify-between p-4 bg-[var(--surface-2)] border border-[var(--border)] rounded-xl group hover:border-[var(--border-strong)] transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 bg-[var(--surface-3)] border border-[var(--border)] rounded-lg flex items-center justify-center shrink-0">
                          <FileText className="w-4 h-4 text-[var(--text-2)]" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-[var(--text-1)] truncate max-w-[220px]">{file.name}</p>
                          <p className="text-xs text-[var(--text-3)]">{fmt(file.size)}</p>
                        </div>
                      </div>
                      {file.preview && (
                        <audio src={file.preview} controls className="h-8 w-32 hidden sm:block opacity-70" />
                      )}
                      <button
                        onClick={() => removeFile(file.id)}
                        className="p-2 text-[var(--text-3)] hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors ml-2"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Voice name + Analyze button */}
            <div className="mt-8 border-t border-[var(--border)] pt-8">
              <h3 className="text-sm font-medium text-[var(--text-2)] mb-4">Voice Configuration</h3>
              <div className="flex flex-col sm:flex-row items-stretch gap-4">
                <input
                  value={voiceName}
                  onChange={e => setVoiceName(e.target.value)}
                  placeholder="Enter a name for this voice…"
                  className="flex-1 bg-[var(--surface-2)] border border-[var(--border)] text-[var(--text-1)] px-4 py-3 rounded-xl focus:outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-3)] text-sm"
                />
                <button
                  onClick={handleAnalyze}
                  disabled={!canAnalyze}
                  className="bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-xl font-medium disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors whitespace-nowrap text-sm"
                >
                  {isUploading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                      Analyzing…
                    </>
                  ) : (
                    <>
                      <Activity className="w-4 h-4" />
                      Analyze Spectral Features
                    </>
                  )}
                </button>
              </div>

              {/* Loading bars */}
              <AnimatePresence>
                {isUploading && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-5 space-y-2"
                  >
                    {['Mel Spectrogram', 'MFCC Extraction', 'Spectral Centroid', 'F0 Estimation'].map((step, i) => (
                      <div key={step} className="flex items-center gap-3">
                        <span className="text-xs text-[var(--text-3)] w-36 shrink-0">{step}</span>
                        <div className="flex-1 h-1 bg-[var(--surface-3)] rounded-full overflow-hidden">
                          <motion.div
                            className="h-full bg-[var(--accent)] rounded-full"
                            initial={{ width: 0 }}
                            animate={{ width: '100%' }}
                            transition={{ delay: i * 0.4, duration: 1.2, ease: 'easeOut' }}
                          />
                        </div>
                      </div>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Result */}
              <AnimatePresence>
                {spectralOk !== null && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    className={`mt-6 p-5 rounded-xl border flex items-start gap-3 ${spectralOk ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-red-500/10 border-red-500/20'}`}
                  >
                    {spectralOk ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
                    )}
                    <div>
                      <p className={`text-sm font-semibold ${spectralOk ? 'text-emerald-400' : 'text-red-400'}`}>
                        {spectralOk ? 'Spectral Analysis Passed' : 'Analysis Failed'}
                      </p>
                      <p className={`text-xs mt-1 ${spectralOk ? 'text-emerald-400/70' : 'text-red-400/70'}`}>
                        {spectralOk
                          ? `Spectral features successfully extracted for "${voiceName}". Ready to submit for training.`
                          : 'Could not extract valid spectral features. Ensure the audio is clean and properly formatted.'}
                      </p>
                      {spectralOk && (
                        <button className="mt-4 inline-flex items-center gap-2 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 text-xs font-medium px-4 py-2 rounded-lg transition-colors">
                          Submit for Training <ChevronRight className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

          {/* Sidebar: Tips */}
          <motion.div
            initial="hidden"
            animate="visible"
            variants={stagger}
            className="space-y-4"
          >
            <motion.div variants={fadeUp} className="bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Info className="w-4 h-4 text-[var(--accent)]" />
                <h3 className="text-sm font-semibold">Recording Tips</h3>
              </div>
              <ul className="space-y-3">
                {TIPS.map((tip, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-[var(--text-2)] leading-relaxed">
                    <div className="w-4 h-4 rounded-full bg-[var(--surface-2)] border border-[var(--border)] flex items-center justify-center shrink-0 mt-0.5 text-[10px] font-bold text-[var(--text-3)]">
                      {i + 1}
                    </div>
                    {tip}
                  </li>
                ))}
              </ul>
            </motion.div>

            <motion.div variants={fadeUp} className="bg-[var(--surface-1)] border border-[var(--border)] rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <Activity className="w-4 h-4 text-sky-400" />
                <h3 className="text-sm font-semibold">What we analyze</h3>
              </div>
              <ul className="space-y-2">
                {['Mel spectrogram', 'MFCC coefficients', 'Spectral centroid', 'Fundamental frequency (F0)', 'Zero-crossing rate'].map(item => (
                  <li key={item} className="flex items-center gap-2 text-xs text-[var(--text-2)]">
                    <div className="w-1.5 h-1.5 rounded-full bg-sky-400/60" />
                    {item}
                  </li>
                ))}
              </ul>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}

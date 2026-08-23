'use client'

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import {
  ShieldCheck,
  AlertTriangle,
  Lock,
  Eye,
  Shield,
  FileText,
  Zap
} from 'lucide-react'

export default function SecurityPage() {
  return (
    <div className="min-h-screen pt-24 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center gap-4"
        >
          <div className="w-12 h-12 rounded-xl bg-[var(--accent)] flex items-center justify-center">
            <ShieldCheck className="h-6 w-6 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-poppins font-bold text-[var(--text-1)]">Security Center</h1>
            <p className="text-[var(--text-2)]">Your account, voices, and generations at a glance</p>
          </div>
        </motion.div>

        {/* Status cards */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {[
            {
              title: '2FA',
              value: 'Enabled',
              icon: Lock,
              tone: 'text-[#22c55e]',
            },
            {
              title: 'Watermarking',
              value: 'Active',
              icon: Shield,
              tone: 'text-[#22c55e]',
            },
            {
              title: 'Active Licenses',
              value: '3',
              icon: FileText,
              tone: 'text-[#3b82f6]',
            },
            {
              title: 'Alerts (30d)',
              value: '0',
              icon: AlertTriangle,
              tone: 'text-[#10b981]',
            },
          ].map((c, i) => {
            const Icon = c.icon
            return (
              <div key={c.title} className="surface-card p-5">
                <div className="flex items-center gap-3 mb-2">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center bg-[var(--surface-2)] ${c.tone}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <span className="text-sm text-[var(--text-2)]">{c.title}</span>
                </div>
                <div className="text-2xl font-semibold text-[var(--text-1)]">{c.value}</div>
              </div>
            )
          })}
        </motion.div>

        {/* Recent activity */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-1 lg:grid-cols-3 gap-6"
        >
          <div className="lg:col-span-2 surface-card p-6">
            <h2 className="text-lg font-semibold text-[var(--text-1)] mb-4">Recent Activity</h2>
            <ul className="divide-y divide-[var(--border)]">
              {[ 
                { id: 1, title: 'Login verified', meta: 'New device · 2 hours ago' },
                { id: 2, title: 'License updated', meta: 'Voice “Atlas” · yesterday' },
                { id: 3, title: 'Generation watermarked', meta: 'Project “Promo” · 2 days ago' },
              ].map(item => (
                <li key={item.id} className="py-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-[var(--text-1)]">{item.title}</p>
                    <p className="text-xs text-[var(--text-2)]">{item.meta}</p>
                  </div>
                  <Eye className="h-4 w-4 text-[var(--text-3)]" />
                </li>
              ))}
            </ul>
          </div>

          <div className="surface-card p-6">
            <h2 className="text-lg font-semibold text-[var(--text-1)] mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Link href="/licensing" className="flex items-center justify-between px-4 py-3 rounded-xl surface-card hover:border-[var(--accent)] transition">
                <div className="flex items-center gap-3">
                  <Shield className="h-5 w-5 text-[var(--accent)]" />
                  <span className="text-sm text-[var(--text-1)]">Manage Voice Permissions</span>
                </div>
                <Zap className="h-4 w-4 text-[var(--text-3)]" />
              </Link>
              <Link href="/help" className="flex items-center justify-between px-4 py-3 rounded-xl surface-card hover:border-[#f59e0b] transition">
                <div className="flex items-center gap-3">
                  <AlertTriangle className="h-5 w-5 text-[#f59e0b]" />
                  <span className="text-sm text-[var(--text-1)]">Report Security Issue</span>
                </div>
                <Zap className="h-4 w-4 text-[var(--text-3)]" />
              </Link>
              <Link href="/dashboard" className="flex items-center justify-between px-4 py-3 rounded-xl surface-card hover:border-[#3b82f6] transition">
                <div className="flex items-center gap-3">
                  <FileText className="h-5 w-5 text-[#3b82f6]" />
                  <span className="text-sm text-[var(--text-1)]">View Usage Logs</span>
                </div>
                <Zap className="h-4 w-4 text-[var(--text-3)]" />
              </Link>
            </div>
          </div>
        </motion.div>
        {/* Verification / Deepfake Detection */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="surface-card p-6 border-t-4"
          style={{ borderTopColor: 'var(--accent)' }}
        >
          <div className="flex items-center gap-3 mb-6">
            <Zap className="h-6 w-6 text-[var(--accent)]" />
            <h2 className="text-xl font-bold text-[var(--text-1)]">6-Layer Deepfake Analysis</h2>
          </div>
          <p className="text-[var(--text-2)] mb-6 text-sm max-w-2xl">
            Upload any audio clip to run it through our military-grade defense mechanism. We analyze acoustics, prosody, paralinguistics, semantics, and verify cryptographic watermarks in real-time.
          </p>

          <DeepfakeAnalyzer />
        </motion.div>

      </div>
    </div>
  )
}

function DeepfakeAnalyzer() {
  const [file, setFile] = React.useState<File | null>(null)
  const [loading, setLoading] = React.useState(false)
  const [result, setResult] = React.useState<any>(null)
  const [error, setError] = React.useState<string | null>(null)

  const handleVerify = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const { verifyAudio } = await import('@/lib/api')
      const res = await verifyAudio(file)
      setResult(res)
    } catch (err: any) {
      setError(err.message || 'Verification failed. Ensure you are logged in as a premium user.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <input 
          type="file" 
          accept="audio/*" 
          onChange={e => setFile(e.target.files?.[0] || null)}
          className="block w-full max-w-sm text-sm text-[var(--text-2)]
            file:mr-4 file:py-2.5 file:px-4
            file:rounded-xl file:border-0
            file:text-sm file:font-semibold
            file:bg-[var(--surface-2)] file:text-[var(--text-1)]
            hover:file:bg-[var(--surface-3)] transition-colors"
        />
        <button 
          onClick={handleVerify}
          disabled={!file || loading}
          className="btn btn-primary px-6 py-2.5"
        >
          {loading ? 'Analyzing...' : 'Run Analysis'}
        </button>
      </div>

      {error && <div className="text-[#ef4444] text-sm">{error}</div>}

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
          <div className="col-span-full mb-2">
            <h3 className="text-lg font-bold text-[var(--text-1)] flex items-center gap-2">
              Final Decision: 
              <span className={`tracking-wider ${result.verdict?.includes('Human') ? 'text-[#22c55e]' : result.verdict?.includes('Watermarked') ? 'text-[#3b82f6]' : 'text-[#ef4444]'}`}>
                {result.verdict}
              </span>
            </h3>
            <p className="text-sm font-medium text-[var(--text-2)]">Overall Authenticity: {((result.overall_authenticity_score || 0) * 100).toFixed(1)}%</p>
          </div>

          <LayerCard title="1. Anti-Spoof (Acoustics)" data={result.layers?.layer1_antispoof} scoreField="spoof_score" invert />
          <LayerCard title="2. Speaker Identity" data={result.layers?.layer2_speaker} scoreField="similarity_score" />
          <LayerCard title="3. Prosody (Pitch Stability)" data={result.layers?.layer3_prosody} scoreField="authenticity_score" />
          <LayerCard title="4. Paralinguistic (Emotion)" data={result.layers?.layer4_paralinguistic} scoreField="authenticity_score" />
          <LayerCard title="5. Semantic (Whisper)" data={result.layers?.layer5_semantic} scoreField="authenticity_score" />
          <div className="surface-card p-4">
            <h4 className="text-sm font-semibold text-[var(--text-1)] mb-2">6. Watermark Detection</h4>
            <div className="text-2xl font-bold text-[#3b82f6]">{result.layers?.layer6_watermark?.found ? 'DETECTED' : 'Not Found'}</div>
          </div>
        </div>
      )}
    </div>
  )
}

function LayerCard({ title, data, scoreField, invert = false }: { title: string, data: any, scoreField: string, invert?: boolean }) {
  if (!data || data.status === 'skipped') {
    return (
      <div className="surface-card p-4 border-l-4 border-l-gray-500">
        <h4 className="text-sm font-semibold text-[var(--text-1)] mb-1">{title}</h4>
        <div className="text-xl font-bold text-[var(--text-2)] mb-2">Skipped</div>
      </div>
    )
  }
  if (data.error) {
    return (
      <div className="surface-card p-4 border-l-4 border-l-[#f59e0b]">
        <h4 className="text-sm font-semibold text-[var(--text-1)] mb-1">{title}</h4>
        <div className="text-sm text-[#f59e0b] mb-2">Error</div>
        <div className="text-xs text-[var(--text-3)] overflow-auto max-h-24">
          {data.error}
        </div>
      </div>
    )
  }
  const score = data[scoreField] || 0;
  const displayScore = invert ? (1 - score) : score;
  const isSuspicious = displayScore < 0.5;

  return (
    <div className={`surface-card p-4 border-l-4 ${isSuspicious ? 'border-l-[#ef4444]' : 'border-l-[#22c55e]'}`}>
      <h4 className="text-sm font-semibold text-[var(--text-1)] mb-1">{title}</h4>
      <div className="text-xl font-bold text-[var(--text-1)] mb-2">Score: {(score * 100).toFixed(1)}%</div>
      <div className="text-xs text-[var(--text-3)] font-mono overflow-auto max-h-24">
        {JSON.stringify(data.details || data.features || data, null, 2)}
      </div>
    </div>
  )
}

'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { 
  Mic, 
  PlayCircle, 
  BarChart3, 
  Plus, 
  Download, 
  Eye,
  TrendingUp,
  Volume2,
  Zap,
  Shield,
  Star
} from 'lucide-react'

export default function DashboardPage() {
  const [selectedPeriod, setSelectedPeriod] = useState('7d')

  // Mock data - replace with real API calls
  const stats = [
    { 
      title: 'Total Voices', 
      value: '12', 
      change: '+2 this week',
      icon: Mic,
      color: 'text-purple-400',
      bg: 'bg-purple-500/10',
      trend: 'up'
    },
    { 
      title: 'Audio Generated', 
      value: '1.2K', 
      change: '+18% vs last week',
      icon: Volume2,
      color: 'text-blue-400',
      bg: 'bg-blue-500/10',
      trend: 'up'
    },
    { 
      title: 'API Calls', 
      value: '8.7K', 
      change: '+24% vs last week',
      icon: Zap,
      color: 'text-yellow-400',
      bg: 'bg-yellow-500/10',
      trend: 'up'
    },
    { 
      title: 'Revenue', 
      value: '$342', 
      change: '+12% vs last week',
      icon: TrendingUp,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      trend: 'up'
    }
  ]

  const recentVoices = [
    { id: 1, name: 'Professional Narrator', status: 'Ready', createdAt: '2024-01-15', usage: 145 },
    { id: 2, name: 'Casual Friend', status: 'Training', createdAt: '2024-01-14', usage: 89 },
    { id: 3, name: 'News Anchor', status: 'Ready', createdAt: '2024-01-12', usage: 267 },
    { id: 4, name: 'Character Voice', status: 'Ready', createdAt: '2024-01-10', usage: 156 }
  ]

  const recentActivity = [
    { id: 1, action: 'Voice generated', voice: 'Professional Narrator', time: '2 hours ago', icon: Volume2 },
    { id: 2, action: 'New voice created', voice: 'Casual Friend', time: '1 day ago', icon: Plus },
    { id: 3, action: 'API key generated', voice: null, time: '2 days ago', icon: Shield },
    { id: 4, action: 'License purchased', voice: 'News Anchor', time: '3 days ago', icon: Star }
  ]

  return (
    <div className="min-h-screen pt-24 pb-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-[var(--text-1)] tracking-tight mb-2">
                Welcome back! 👋
              </h1>
              <p className="text-[var(--text-2)]">
                Here's what's happening with your voice clones today
              </p>
            </div>
            
            <div className="flex items-center space-x-3 mt-4 sm:mt-0">
              <select 
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="bg-[var(--surface)] border border-[var(--border)] text-[var(--text-1)] rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-[var(--text-2)] transition-colors cursor-pointer"
              >
                <option value="1d">Last 24 hours</option>
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 90 days</option>
              </select>
              
              <Link 
                href="/training"
                className="bg-white text-black hover:bg-gray-200 transition-colors font-medium px-4 py-2 rounded-lg text-sm inline-flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>New Voice</span>
              </Link>
            </div>
          </div>
        </motion.div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={stat.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 * index }}
                className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6 hover:border-gray-700 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="text-sm font-medium text-[var(--text-2)] mb-1">{stat.title}</p>
                    <p className="text-2xl font-bold text-[var(--text-1)] mb-1 tracking-tight">{stat.value}</p>
                    <p className="text-xs text-emerald-400 flex items-center font-medium">
                      <TrendingUp className="w-3 h-3 mr-1" />
                      {stat.change}
                    </p>
                  </div>
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${stat.bg}`}>
                    <Icon className={`w-5 h-5 ${stat.color}`} />
                  </div>
                </div>
              </motion.div>
            )
          })}
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Recent Voices */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6 h-full"
            >
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-[var(--text-1)]">Your Voices</h2>
                <Link href="/training" className="text-[var(--text-2)] hover:text-white text-sm font-medium transition-colors">
                  View All →
                </Link>
              </div>
              
              <div className="space-y-3">
                {recentVoices.map((voice, index) => (
                  <motion.div
                    key={voice.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: 0.1 * index }}
                    className="flex items-center justify-between p-4 border border-[var(--border)] rounded-lg hover:bg-white/5 transition-colors group cursor-pointer"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-10 h-10 bg-white/5 rounded-lg flex items-center justify-center border border-white/5 group-hover:bg-white/10 transition-colors">
                        <Mic className="w-4 h-4 text-[var(--text-1)]" />
                      </div>
                      <div>
                        <h3 className="font-medium text-[var(--text-1)]">{voice.name}</h3>
                        <p className="text-xs text-[var(--text-2)] mt-0.5">
                          Created {voice.createdAt} • {voice.usage} uses
                        </p>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-4">
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-medium uppercase tracking-wider ${
                        voice.status === 'Ready' 
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                          : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
                      }`}>
                        {voice.status}
                      </span>
                      
                      <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-[var(--text-2)] hover:text-white">
                          <PlayCircle className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-[var(--text-2)] hover:text-white">
                          <Eye className="w-4 h-4" />
                        </button>
                        <button className="p-1.5 hover:bg-white/10 rounded-md transition-colors text-[var(--text-2)] hover:text-white">
                          <Download className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6"
            >
              <h2 className="text-lg font-semibold text-[var(--text-1)] mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <Link 
                  href="/training"
                  className="flex items-center space-x-3 p-3 border border-transparent hover:border-[var(--border)] hover:bg-white/5 rounded-lg transition-all group"
                >
                  <div className="w-8 h-8 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Plus className="w-4 h-4 text-[var(--text-1)]" />
                  </div>
                  <span className="font-medium text-sm text-[var(--text-1)]">Create New Voice</span>
                </Link>
                
                <Link 
                  href="/playground"
                  className="flex items-center space-x-3 p-3 border border-transparent hover:border-[var(--border)] hover:bg-white/5 rounded-lg transition-all group"
                >
                  <div className="w-8 h-8 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <PlayCircle className="w-4 h-4 text-[var(--text-1)]" />
                  </div>
                  <span className="font-medium text-sm text-[var(--text-1)]">Try Playground</span>
                </Link>
                
                <Link 
                  href="/billing"
                  className="flex items-center space-x-3 p-3 border border-transparent hover:border-[var(--border)] hover:bg-white/5 rounded-lg transition-all group"
                >
                  <div className="w-8 h-8 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform">
                    <BarChart3 className="w-4 h-4 text-[var(--text-1)]" />
                  </div>
                  <span className="font-medium text-sm text-[var(--text-1)]">View Analytics</span>
                </Link>
              </div>
            </motion.div>

            {/* Recent Activity */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="bg-[var(--surface)] border border-[var(--border)] rounded-xl p-6"
            >
              <h2 className="text-lg font-semibold text-[var(--text-1)] mb-4">Recent Activity</h2>
              <div className="space-y-5">
                {recentActivity.map((activity, index) => {
                  const Icon = activity.icon
                  return (
                    <motion.div
                      key={activity.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: 0.1 * index }}
                      className="flex items-start space-x-3"
                    >
                      <div className="w-8 h-8 bg-white/5 border border-white/10 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5">
                        <Icon className="w-3.5 h-3.5 text-[var(--text-2)]" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-[var(--text-1)] leading-snug">
                          <span className="font-medium">{activity.action}</span>
                          {activity.voice && (
                            <span className="text-[var(--text-2)]"> for {activity.voice}</span>
                          )}
                        </p>
                        <p className="text-[11px] text-[var(--text-2)] mt-1 tracking-wide uppercase">{activity.time}</p>
                      </div>
                    </motion.div>
                  )
                })}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

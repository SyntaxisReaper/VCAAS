'use client'

import { Cog6ToothIcon } from '@heroicons/react/24/outline'

interface TrainingConfig {
  voiceName: string
  language: string
  description: string
  isPublic: boolean
  trainingSettings: {
    epochs: number
    learningRate: number
    batchSize: number
    clipDuration: number
  }
}

interface TrainingConfigFormProps {
  config: TrainingConfig
  onChange: (config: TrainingConfig) => void
}

export default function TrainingConfigForm({ config, onChange }: TrainingConfigFormProps) {
  const handleConfigChange = (key: keyof TrainingConfig, value: any) => {
    const newConfig = {
      ...config,
      [key]: value
    }
    onChange(newConfig)
  }

  const handleTrainingSettingChange = (key: keyof TrainingConfig['trainingSettings'], value: number) => {
    const newConfig = {
      ...config,
      trainingSettings: {
        ...config.trainingSettings,
        [key]: value
      }
    }
    onChange(newConfig)
  }

  // Ensure input values are properly controlled
  const handleVoiceNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault()
    const value = e.target.value
    handleConfigChange('voiceName', value)
  }

  const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    e.preventDefault()
    const value = e.target.value
    handleConfigChange('description', value)
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-medium text-gray-900 mb-6">Training Configuration</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice Name *
          </label>
          <input
            type="text"
            value={config.voiceName || ''}
            onChange={handleVoiceNameChange}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 bg-white text-gray-900"
            placeholder="My Professional Voice"
            autoComplete="off"
            spellCheck={false}
            name="voiceName"
            id="voiceName"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          <select
            value={config.language || 'en'}
            onChange={(e) => handleConfigChange('language', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 bg-white text-gray-900"
            autoComplete="off"
            name="language"
            id="language"
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
            <option value="it">Italian</option>
            <option value="pt">Portuguese</option>
          </select>
        </div>

        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description
          </label>
          <textarea
            value={config.description || ''}
            onChange={handleDescriptionChange}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 bg-white resize-none text-gray-900"
            placeholder="Describe the characteristics of this voice..."
            autoComplete="off"
            spellCheck={false}
            name="description"
            id="description"
          />
        </div>

        <div className="md:col-span-2">
          <div className="flex items-center">
            <input
              id="is-public"
              type="checkbox"
              checked={config.isPublic}
              onChange={(e) => handleConfigChange('isPublic', e.target.checked)}
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="is-public" className="ml-2 text-sm text-gray-700">
              Make this voice publicly available for licensing
            </label>
          </div>
        </div>
      </div>

      {/* Advanced Settings */}
      <div className="mt-8 border-t pt-6">
        <h3 className="text-md font-medium text-gray-900 mb-4 flex items-center">
          <Cog6ToothIcon className="h-5 w-5 mr-2" />
          Advanced Training Settings
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Training Epochs
            </label>
            <input
              type="number"
              value={config.trainingSettings.epochs || 100}
              onChange={(e) => handleTrainingSettingChange('epochs', parseInt(e.target.value) || 100)}
              min="50"
              max="1000"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 bg-white text-gray-900"
              autoComplete="off"
              name="epochs"
              id="epochs"
            />
            <p className="text-xs text-gray-500 mt-1">More epochs = better quality, longer training time</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Learning Rate
            </label>
            <input
              type="number"
              value={config.trainingSettings.learningRate || 0.0002}
              onChange={(e) => handleTrainingSettingChange('learningRate', parseFloat(e.target.value) || 0.0002)}
              min="0.0001"
              max="0.01"
              step="0.0001"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500 bg-white text-gray-900"
              autoComplete="off"
              name="learningRate"
              id="learningRate"
            />
          </div>
        </div>
      </div>
    </div>
  )
}

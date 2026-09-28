'use client'

import type { Prediction } from '@/types/prediction'
import { CheckCircle, XCircle, Leaf, Shield, AlertTriangle, FileText, Clock } from 'lucide-react'

interface Props {
  data: Prediction | null
}

export default function ResultPanel({ data }: Props) {
  if (!data) {
    return (
      <div className="space-y-2">
        <h2 className="text-lg font-semibold">Prediction Result</h2>
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No prediction yet. Upload an image to see results.
        </p>
      </div>
    )
  }

  const plant = data.plant
  const health = data.health
  const disease = data.disease
  const isDiseased = health.label === 'Diseased'

  // Helper for progress bar
  const ProgressBar = ({ value, color }: { value: number, color: string }) => (
    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden mt-1">
      <div
        className={`${color} h-full rounded-full transition-all duration-300 block`}
        style={{ width: `${Math.round(value * 100)}%` }}
      />
    </div>
  )

  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold flex items-center gap-2">
        <Shield className="w-6 h-6 text-emerald-500" /> Prediction Result
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Plant */}
        <div className="rounded-2xl border border-gray-200 dark:border-gray-800 p-4 bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/30 dark:to-green-800/30 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <Leaf className="w-5 h-5 text-green-600" />
            <span className="font-semibold text-green-800 dark:text-green-200">Plant</span>
          </div>
          <div className="text-lg font-bold mb-1">{plant.label}</div>
          <ProgressBar value={plant.confidence} color="bg-green-400" />
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-2">Top-3: {plant.top3.map(([l, c]) => `${l} (${(c*100).toFixed(1)}%)`).join(', ')}</div>
        </div>
        {/* Health */}
        <div className={`rounded-2xl border border-gray-200 dark:border-gray-800 p-4 bg-gradient-to-br ${isDiseased ? 'from-red-50 to-red-100 dark:from-red-900/30 dark:to-red-800/30' : 'from-emerald-50 to-emerald-100 dark:from-emerald-900/30 dark:to-emerald-800/30'} shadow-sm`}>
          <div className="flex items-center gap-2 mb-2">
            {isDiseased ? <AlertTriangle className="w-5 h-5 text-red-600" /> : <CheckCircle className="w-5 h-5 text-emerald-600" />}
            <span className={`font-semibold ${isDiseased ? 'text-red-800 dark:text-red-200' : 'text-emerald-800 dark:text-emerald-200'}`}>Health</span>
          </div>
          <div className={`text-lg font-bold mb-1 ${isDiseased ? 'text-red-700 dark:text-red-200' : 'text-emerald-700 dark:text-emerald-200'}`}>{health.label}</div>
          <ProgressBar value={health.confidence} color={isDiseased ? 'bg-red-400' : 'bg-emerald-400'} />
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-2">Top-3: {health.top3.map(([l, c]) => `${l} (${(c*100).toFixed(1)}%)`).join(', ')}</div>
        </div>
        {/* Disease */}
        <div className="rounded-2xl border border-gray-200 dark:border-gray-800 p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/30 dark:to-yellow-800/30 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <XCircle className="w-5 h-5 text-yellow-600" />
            <span className="font-semibold text-yellow-800 dark:text-yellow-200">Disease</span>
          </div>
          <div className="text-lg font-bold mb-1">{disease.label}</div>
          <ProgressBar value={disease.confidence} color="bg-yellow-400" />
          <div className="text-xs text-gray-600 dark:text-gray-300 mt-2">Top-3: {disease.top3.map(([l, c]) => `${l} (${(c*100).toFixed(1)}%)`).join(', ')}</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className={`rounded-xl border border-gray-200 dark:border-gray-800 p-3 flex items-center gap-2 ${data.spray ? 'bg-red-50 dark:bg-red-900/20' : 'bg-emerald-50 dark:bg-emerald-900/20'}`}>
          {data.spray ? <AlertTriangle className="w-5 h-5 text-red-600" /> : <CheckCircle className="w-5 h-5 text-emerald-600" />}
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Spray Action</p>
            <p className={`text-sm font-semibold ${data.spray ? 'text-red-600 dark:text-red-300' : 'text-emerald-600 dark:text-emerald-300'}`}>
              {data.spray ? 'SPRAY (1)' : 'NO SPRAY (0)'}
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-3 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-500 dark:text-gray-300" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">File</p>
            <p className="text-sm font-medium truncate">{data.fileName ?? '—'}</p>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-3 col-span-2 flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-500 dark:text-gray-300" />
          <div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Timestamp</p>
            <p className="text-sm font-medium">{data.at ? new Date(data.at).toLocaleString() : '—'}</p>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        * Decision policy: If health is <em>Diseased</em> and confidence &gt;= <span className="font-mono">0.60</span>, spray = 1.<br />
        <span className="text-[10px] text-gray-400">[Debug] Health label: <b>{health.label}</b>, Health confidence: <b>{(health.confidence*100).toFixed(1)}%</b>, Spray: <b>{data.spray}</b></span>
      </p>
    </div>
  )
}

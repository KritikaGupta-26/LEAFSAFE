'use client'

import type { Prediction } from '@/types/prediction'

interface Props {
  items: Prediction[]
}

export default function History({ items }: Props) {
  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">History (last 10)</h2>

      {items.length === 0 ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No history yet. Predictions will appear here.
        </p>
      ) : (
        <ul className="space-y-2">
          {items.map((it, idx) => {
            const isInfected = it.label === 'Infected'
            const confidencePct = Math.round((it.confidence ?? 0) * 100)
            return (
              <li
                key={`${it.at ?? idx}-${it.fileName ?? idx}`}
                className="flex items-center justify-between gap-3 rounded-xl border border-gray-200 dark:border-gray-800 p-3"
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        isInfected
                          ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200'
                          : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200'
                      }`}
                    >
                      {it.label}
                    </span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">
                      {confidencePct}% confidence
                    </span>
                  </div>
                  <p className="text-sm font-medium truncate mt-1">
                    {it.fileName ?? '—'}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                    {it.at ? new Date(it.at).toLocaleString() : '—'}
                  </p>
                </div>

                <div className="shrink-0 text-right">
                  <span
                    className={`inline-flex items-center rounded-md px-2 py-1 text-xs font-semibold border ${
                      it.spray
                        ? 'border-red-300/60 text-red-600 dark:text-red-300'
                        : 'border-emerald-300/60 text-emerald-600 dark:text-emerald-300'
                    }`}
                  >
                    {it.spray ? 'SPRAY (1)' : 'NO SPRAY (0)'}
                  </span>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </div>
  )
}

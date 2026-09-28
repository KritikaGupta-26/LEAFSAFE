'use client'

import { useState } from 'react'
import Upload from '@/components/upload'
import ResultPanel from '@/components/ResultPanel'
import History from '@/components/History'
import IoTSimulation from '@/components/IOTSimulation'
import type { Prediction } from '@/types/prediction'

export default function Page() {
  const [prediction, setPrediction] = useState<Prediction | null>(null)
  const [history, setHistory] = useState<Prediction[]>([])
  const [spray, setSpray] = useState<0 | 1>(0)

  const handlePrediction = (p: Prediction) => {
    setPrediction(p)
    setHistory((prev) => [p, ...prev].slice(0, 10))
    // Always reset spray to 0 before setting to 1 to force animation
    setSpray(0)
    if (p.spray === 1) {
      setTimeout(() => setSpray(1), 50)
      // Optionally reset to 0 after animation completes (2s + buffer)
      setTimeout(() => setSpray(0), 2100)
    }
  }

  return (
    <div className="grid gap-6 md:grid-cols-5">
      {/* Left side: upload + history */}
      <section className="md:col-span-3 space-y-6">
        <div className="card p-5">
          <Upload onPredicted={handlePrediction} />
        </div>
        <div className="card p-5">
          <History items={history} />
        </div>
      </section>

      {/* Right side: result + IoT simulation */}
      <aside className="md:col-span-2 space-y-6">
        <div className="card p-5">
          <ResultPanel data={prediction} />
        </div>
        <div className="card p-5">
          <IoTSimulation spray={spray} />
        </div>
      </aside>
    </div>
  )
}

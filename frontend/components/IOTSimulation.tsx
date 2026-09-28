'use client'

import { useEffect, useMemo, useState } from 'react'
import { Cpu, Power, Activity } from 'lucide-react'

interface Props {
  /** 0 = no spray, 1 = spray */
  spray: 0 | 1
}

/**
 * Visual-only simulation of the ESP32 state:
 * - LED: ON when spray=1
 * - Servo: animates to 90° when spray=1, returns to 0° afterward
 */
export default function IoTSimulation({ spray }: Props) {
  const [ledOn, setLedOn] = useState(false)
  const [servoAngle, setServoAngle] = useState(0)

  useEffect(() => {
    let t: NodeJS.Timeout | undefined
    if (spray === 1) {
      setLedOn(true)
      setServoAngle(0) // reset to 0 before animating
      setTimeout(() => {
        setServoAngle(90)
        t = setTimeout(() => setServoAngle(0), 2000)
      }, 10)
    } else {
      setLedOn(false)
      setServoAngle(0)
    }
    return () => {
      if (t) clearTimeout(t)
    }
  }, [spray])

  const status = useMemo(
    () =>
      spray === 1
        ? { label: 'SPRAYING', cls: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-200' }
        : { label: 'IDLE', cls: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-200' },
    [spray]
  )

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold">IoT Simulation (ESP32)</h2>

      {/* Status pill */}
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${status.cls}`}>
          {status.label}
        </span>
        <span className="inline-flex items-center gap-1 text-xs text-gray-600 dark:text-gray-400">
          <Activity className="w-3.5 h-3.5" />
          Serial Command: {spray}
        </span>
      </div>

      {/* Panels */}
      <div className="grid grid-cols-2 gap-3">
        {/* LED */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">LED</p>
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ring-2 ${
                ledOn
                  ? 'bg-red-500 ring-red-300/60'
                  : 'bg-gray-300 dark:bg-gray-700 ring-gray-300/40 dark:ring-gray-700/60'
              }`}
              aria-label={ledOn ? 'LED on' : 'LED off'}
            />
            <p className="text-sm font-medium">{ledOn ? 'ON' : 'OFF'}</p>
          </div>
        </div>

        {/* Servo */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-3">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Servo (°)</p>
          <p className="text-sm font-semibold">{servoAngle}°</p>
          <div className="mt-2 h-2 w-full rounded-full bg-gray-200 dark:bg-gray-800">
            <div
              className="h-2 rounded-full bg-emerald-400 transition-all duration-500"
              style={{ width: `${(servoAngle / 180) * 100}%` }}
            />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Debug: Servo bar width = {(servoAngle / 180 * 100).toFixed(1)}% | spray prop: {spray}</p>
        </div>

        {/* Board */}
        <div className="rounded-xl border border-gray-200 dark:border-gray-800 p-3 col-span-2">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">Board</p>
          <div className="flex items-center gap-3 text-sm">
            <span className="inline-flex items-center gap-1.5">
              <Cpu className="w-4 h-4" /> ESP32 (simulated)
            </span>
            <span className="inline-flex items-center gap-1.5 text-gray-600 dark:text-gray-400">
              <Power className="w-4 h-4" /> {spray ? 'Relay ON' : 'Relay OFF'}
            </span>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Behavior: When <code>spray=1</code>, LED turns ON and servo moves to 90° for ~2s, then returns to 0°.
          </p>
        </div>
      </div>
    </div>
  )
}
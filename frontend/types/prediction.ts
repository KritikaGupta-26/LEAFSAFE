export type HeadResult = {
  label: string
  confidence: number
  top3: [string, number][]
}

export type Prediction = {
  plant: HeadResult
  health: HeadResult
  disease: HeadResult
  spray: 0 | 1
  fileName?: string
  at?: string // ISO timestamp
  predictionKey?: string // for UI animation uniqueness
}

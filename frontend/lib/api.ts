import axios from 'axios'
import type { Prediction } from '@/types/prediction'

const BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://127.0.0.1:8000'

export async function predictImage(file: File): Promise<Prediction> {
  const form = new FormData()
  form.append('file', file)

  const res = await axios.post(`${BASE}/predict`, form)

  // Expecting { plant, health, disease, spray, fileName, at } from FastAPI
  return res.data as Prediction
}

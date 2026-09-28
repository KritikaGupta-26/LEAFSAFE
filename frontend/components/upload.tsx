'use client'

import { useState } from 'react'
import { predictImage } from '@/lib/api'
import type { Prediction } from '@/types/prediction'
import { Upload as UploadIcon } from 'lucide-react'

interface Props {
  onPredicted: (result: Prediction) => void
}

export default function Upload({ onPredicted }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<boolean>(false)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0]
      setFile(selectedFile)
      setError(null)
      // Show image preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result as string)
      }
      reader.readAsDataURL(selectedFile)
    } else {
      setFile(null)
      setPreview(null)
    }
  }

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select an image')
      return
    }
    try {
      setLoading(true)
      setError(null)
      setSuccess(false)
      const res = await predictImage(file)
      // add timestamp and file name for history
  // Store a unique predictionKey for animation, but keep at as a valid ISO string
  res.predictionKey = new Date().toISOString() + '-' + Math.random().toString(36).slice(2, 8)
  res.at = new Date().toISOString()
      res.fileName = file.name
      onPredicted(res)
      setSuccess(true)
    } catch (err) {
      setError('Prediction failed. Is the backend running?')
      setSuccess(false)
    } finally {
      setLoading(false)
    }
  }

  return (
  <div className="space-y-4">
      <h2 className="text-lg font-semibold mb-2">Upload Leaf Image</h2>

      <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div>
          <label htmlFor="file-upload" className="cursor-pointer inline-flex items-center px-4 py-2 bg-gray-800 text-white rounded shadow hover:bg-gray-700 transition">
            <UploadIcon className="w-4 h-4 mr-2" />
            Choose File
          </label>
          <input
            id="file-upload"
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
          />
          {file && (
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              Selected: {file.name}
            </p>
          )}
        </div>

        <button
          onClick={handleSubmit}
          disabled={loading || !file}
          className={`btn-primary ml-0 sm:ml-4 ${loading || !file ? 'opacity-50 cursor-not-allowed' : ''}`}
          aria-disabled={loading || !file}
        >
          {loading ? (
            <>
              <svg className="animate-spin w-4 h-4 mr-2 inline-block" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Predicting...
            </>
          ) : (
            <>
              <UploadIcon className="w-4 h-4 mr-2" />
              Predict
            </>
          )}
        </button>
      </div>

      {preview && (
        <img
          src={preview}
          alt="Preview"
          className="mt-2 rounded shadow max-h-48 border"
        />
      )}

      {error && <p className="text-sm text-red-600" role="alert">{error}</p>}
      {success && !error && (
        <p className="text-sm text-green-600" role="status">Prediction successful!</p>
      )}
    </div>
  )
}

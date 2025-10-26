import { useState, useEffect } from 'react'
import type { Dataset, DatasetAnalysis } from '../types/index'

export const useDatasets = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchDatasets = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/datasets')
      if (!response.ok) throw new Error('Failed to fetch datasets')
      const data = await response.json()
      setDatasets(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch datasets')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDatasets()
  }, [])

  return { datasets, loading, error, refetch: fetchDatasets }
}

export const useDatasetAnalysis = (datasetName: string | undefined) => {
  const [analysis, setAnalysis] = useState<DatasetAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!datasetName) return

    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Try to fetch the analysis JSON directly
        const response = await fetch(`http://localhost:8000/datasets/${datasetName}/${datasetName}-analysis.json`)
        if (!response.ok) throw new Error(`No analysis found for ${datasetName}`)
        
        const data = await response.json()
        setAnalysis(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch analysis')
        setAnalysis(null)
      } finally {
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [datasetName])

  return { analysis, loading, error }
}
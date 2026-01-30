import { useState, useCallback } from 'react'

interface DownloadOptions {
  filename?: string
  mimeType?: string
  autoDownload?: boolean
}

interface DownloadState {
  isDownloading: boolean
  error: Error | null
  progress: number
}

interface DownloadResult {
  download: (data: string | Blob, options?: DownloadOptions) => void
  downloadFromUrl: (url: string, options?: DownloadOptions) => Promise<void>
  downloadFile: (filePath: string, options?: DownloadOptions) => Promise<void>
  state: DownloadState
  reset: () => void
}

export function useDownload(): DownloadResult {
  const [state, setState] = useState<DownloadState>({
    isDownloading: false,
    error: null,
    progress: 0,
  })

  const reset = useCallback(() => {
    setState({ isDownloading: false, error: null, progress: 0 })
  }, [])

  const createDownloadLink = useCallback(
    (data: string | Blob, mimeType: string): { url: string; filename: string } => {
      let blob: Blob
      let filename: string

      if (typeof data === 'string') {
        blob = new Blob([data], { type: mimeType })
        filename = `download-${Date.now()}.${mimeType.split('/')[1] || 'txt'}`
      } else {
        blob = data
        filename = `download-${Date.now()}.${mimeType.split('/')[1] || 'bin'}`
      }

      const url = URL.createObjectURL(blob)
      return { url, filename }
    },
    []
  )

  const triggerDownload = useCallback(
    (url: string, filename: string) => {
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      link.style.display = 'none'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    },
    []
  )

  const download = useCallback(
    (data: string | Blob, options: DownloadOptions = {}) => {
      const { filename, mimeType = 'text/plain', autoDownload = true } = options

      try {
        const { url, filename: generatedFilename } = createDownloadLink(
          data,
          mimeType
        )
        const finalFilename = filename || generatedFilename

        if (autoDownload) {
          triggerDownload(url, finalFilename)
        }

        setState({ isDownloading: false, error: null, progress: 100 })
      } catch (err) {
        setState((prev) => ({
          ...prev,
          error: err instanceof Error ? err : new Error('Download failed'),
        }))
      }
    },
    [createDownloadLink, triggerDownload]
  )

  const downloadFromUrl = useCallback(
    async (url: string, options: DownloadOptions = {}) => {
      setState({ isDownloading: true, error: null, progress: 0 })

      try {
        const response = await fetch(url, { mode: 'cors' })

        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`)
        }

        const blob = await response.blob()
        const mimeType = options.mimeType || blob.type || 'application/octet-stream'

        setState({ isDownloading: true, error: null, progress: 50 })

        const { url: objectUrl, filename: generatedFilename } = createDownloadLink(
          blob,
          mimeType
        )

        const filename = options.filename || generatedFilename

        if (options.autoDownload !== false) {
          triggerDownload(objectUrl, filename)
        }

        setState({ isDownloading: false, error: null, progress: 100 })
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isDownloading: false,
          error: err instanceof Error ? err : new Error('Download from URL failed'),
        }))
      }
    },
    [createDownloadLink, triggerDownload]
  )

  const downloadFile = useCallback(
    async (filePath: string, options: DownloadOptions = {}) => {
      setState({ isDownloading: true, error: null, progress: 0 })

      try {
        const response = await fetch(filePath)

        if (!response.ok) {
          throw new Error(`Failed to fetch file: ${response.status}`)
        }

        const blob = await response.blob()
        const mimeType = options.mimeType || blob.type || 'application/octet-stream'

        setState({ isDownloading: true, error: null, progress: 75 })

        const { url, filename: generatedFilename } = createDownloadLink(
          blob,
          mimeType
        )

        const filename = options.filename || filePath.split('/').pop() || generatedFilename

        if (options.autoDownload !== false) {
          triggerDownload(url, filename)
        }

        setState({ isDownloading: false, error: null, progress: 100 })
      } catch (err) {
        setState((prev) => ({
          ...prev,
          isDownloading: false,
          error: err instanceof Error ? err : new Error('Download file failed'),
        }))
      }
    },
    [createDownloadLink, triggerDownload]
  )

  return {
    download,
    downloadFromUrl,
    downloadFile,
    state,
    reset,
  }
}

export function useDownloadFile() {
  const { download, downloadFromUrl, state, reset } = useDownload()

  const downloadCSV = useCallback(
    (data: string | object[], filename: string) => {
      const csvData =
        typeof data === 'string'
          ? data
          : convertToCSV(data)
      download(csvData, { filename: filename.endsWith('.csv') ? filename : `${filename}.csv`, mimeType: 'text/csv' })
    },
    [download]
  )

  const downloadJSON = useCallback(
    (data: unknown, filename: string, indent: number = 2) => {
      const jsonData = JSON.stringify(data, null, indent)
      download(jsonData, { filename: filename.endsWith('.json') ? filename : `${filename}.json`, mimeType: 'application/json' })
    },
    [download]
  )

  const downloadExcel = useCallback(
    (data: string | Blob, filename: string) => {
      download(data, { filename: filename.endsWith('.xlsx') ? filename : `${filename}.xlsx`, mimeType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    },
    [download]
  )

  const downloadText = useCallback(
    (data: string, filename: string, mimeType: string = 'text/plain') => {
      download(data, { filename, mimeType })
    },
    [download]
  )

  return {
    downloadCSV,
    downloadJSON,
    downloadExcel,
    downloadText,
    downloadFromUrl,
    ...state,
    reset,
  }
}

function convertToCSV(data: object[]): string {
  if (data.length === 0) return ''

  const headers = Object.keys(data[0])
  const rows = data.map((row) =>
    headers.map((header) => {
      const value = (row as Record<string, unknown>)[header]
      const stringValue = String(value ?? '')
      const escaped = stringValue.replace(/"/g, '""')
      return `"${escaped}"`
    }).join(',')
  )

  return [headers.join(','), ...rows].join('\n')
}

export default useDownload

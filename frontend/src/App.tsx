import { useState, useCallback } from 'react'
import './App.css'
import logo from './assets/images/DocMcQueryCapybaraStill.png'
import loadingGif from './assets/gifs/DocMcQueryCapybaraSortingFiles.gif'

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedMedia, setSelectedMedia] = useState<{filename: string, data: any} | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>('')

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)

    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.zip')) {
      setFile(droppedFile)
      setError(null)
    } else {
      setError('Please upload a .zip file')
    }
  }, [])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.name.endsWith('.zip')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setError('Please upload a .zip file')
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/process', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Upload failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="app">
      <nav className="navbar">
        <div className="navbar-left">
          <img src={logo} alt="Ad McQuery Logo" className="logo" />
          <h1>Ad McQuery</h1>
        </div>
      </nav>
      <div className="container">
        {!uploading && !result && <p className="subtitle">Upload a zip file containing .png images and .mp4 videos</p>}

        {!uploading && !result && (
          <div
            className={`dropzone ${isDragging ? 'dragging' : ''} ${file ? 'has-file' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('file-input')?.click()}
          >
            <input
              id="file-input"
              type="file"
              accept=".zip"
              onChange={handleFileInput}
              style={{ display: 'none' }}
            />

            {file ? (
              <div className="file-info">
                <svg className="file-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
                <div>
                  <p className="file-name">{file.name}</p>
                  <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            ) : (
              <div className="dropzone-content">
                <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="dropzone-text">Drag & drop your zip file here</p>
                <p className="dropzone-subtext">or click to browse</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {file && !result && (
          <>
            <button
              className="upload-button"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading ? 'Processing...' : 'Process Zip File'}
            </button>

            {uploading && (
              <div className="loading-container">
                <img src={loadingGif} alt="Processing files..." className="loading-gif" />
                <p className="loading-text">Processing your files...</p>
              </div>
            )}
          </>
        )}

        {result && (
          <div className="result">
            <h2>Ad Analysis Results</h2>

            <div className="search-container">
              <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="11" cy="11" r="8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M21 21l-4.35-4.35" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input
                type="text"
                className="search-input"
                placeholder="Search files by name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              {searchQuery && (
                <button className="search-clear" onClick={() => setSearchQuery('')}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>

            {(() => {
              const filteredEntries = Object.entries(result)
                .filter(([filename]) =>
                  filename.toLowerCase().includes(searchQuery.toLowerCase())
                )
                .sort(([filenameA], [filenameB]) => {
                  const getTypeAndNum = (name: string) => {
                    const match = name.match(/^([a-z]+)(\d+)\./i)
                    return match ? { type: match[1], num: parseInt(match[2]) } : { type: name, num: 0 }
                  }

                  const a = getTypeAndNum(filenameA)
                  const b = getTypeAndNum(filenameB)

                  if (a.type !== b.type) {
                    return a.type.localeCompare(b.type)
                  }
                  return a.num - b.num
                })

              return (
                <>
                  <p className="result-summary">
                    Showing {filteredEntries.length} of {Object.keys(result).length} files
                  </p>

                  {filteredEntries.length === 0 ? (
                    <div className="no-results">
                      <p>No files found matching "{searchQuery}"</p>
                    </div>
                  ) : (
                    <div className="video-grid">
                      {filteredEntries.map(([filename, data]: [string, any]) => (
                        <div key={filename} className="video-container">
                          <div className="video-header">
                            <h3 className="video-filename">{filename}</h3>
                            {data.metadata && (
                              <p className="file-meta">
                                {data.metadata.width} × {data.metadata.height} • {data.metadata.format}
                              </p>
                            )}
                          </div>
                          <div
                            className="video-wrapper"
                            onClick={() => setSelectedMedia({filename, data})}
                            style={{ cursor: 'pointer' }}
                          >
                            {filename.toLowerCase().endsWith('.mp4') ? (
                              <video
                                className="video-player"
                                onError={(e) => {
                                  e.currentTarget.style.display = 'none'
                                }}
                              >
                                <source src={`http://localhost:8000/media/${filename}`} type="video/mp4" />
                                Your browser does not support the video tag.
                              </video>
                            ) : (
                              <img
                                src={`http://localhost:8000/media/${filename}`}
                                alt={filename}
                                className="image-preview"
                                onError={(e) => {
                                  e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="%231a1a1a"/><text x="50%" y="50%" text-anchor="middle" fill="%23888" font-size="16">Image not available</text></svg>'
                                }}
                              />
                            )}
                          </div>
                          <div className="video-info">
                            {data.ocr && data.ocr.text && (
                              <div className="info-section">
                                <h4>Text Content:</h4>
                                <p className="analysis-text">{data.ocr.text}</p>
                              </div>
                            )}
                            {data.contrast && (
                              <div className="info-section">
                                <h4>Contrast Analysis:</h4>
                                <p className="analysis-text">
                                  Mean: {data.contrast.mean?.toFixed(2)}<br />
                                  Std Dev: {data.contrast.std_dev?.toFixed(2)}
                                </p>
                              </div>
                            )}
                            {data.analysis_error && (
                              <div className="info-section error">
                                <h4>Analysis Error:</h4>
                                <p className="analysis-text">{data.analysis_error}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )
            })()}
          </div>
        )}

        {selectedMedia && (
          <div className="modal-overlay" onClick={() => setSelectedMedia(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={() => setSelectedMedia(null)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>

              <div className="modal-media">
                {selectedMedia.filename.toLowerCase().endsWith('.mp4') ? (
                  <video
                    controls
                    autoPlay
                    className="modal-video"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none'
                    }}
                  >
                    <source src={`http://localhost:8000/media/${selectedMedia.filename}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <img
                    src={`http://localhost:8000/media/${selectedMedia.filename}`}
                    alt={selectedMedia.filename}
                    className="modal-image"
                    onError={(e) => {
                      e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600"><rect width="800" height="600" fill="%231a1a1a"/><text x="50%" y="50%" text-anchor="middle" fill="%23888" font-size="24">Image not available</text></svg>'
                    }}
                  />
                )}
              </div>

              <div className="modal-info">
                <h3>{selectedMedia.filename}</h3>
                <p className="modal-sample-text">
                  This is sample text that provides additional information about the ad.
                  It could include analysis results, metrics, or other relevant data about
                  the advertisement performance and content.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

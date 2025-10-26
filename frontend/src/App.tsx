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

                          >
                            {filename.toLowerCase().endsWith('.mp4') ? (
                              <video
                                className="video-player"
                                onError={(e) => {
                                  e.currentTarget.style.display = 'none'
                                }}
                              >
                                <source src={`http://localhost:8000/datasets/ads/videos/${filename}`} type="video/mp4" />
                                Your browser does not support the video tag.
                              </video>
                            ) : (
                              <img
                                src={`http://localhost:8000/datasets/ads/images/${filename}`}
                                alt={filename}
                                className="image-preview"
                                onError={(e) => {
                                  e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300"><rect width="400" height="300" fill="%231a1a1a"/><text x="50%" y="50%" text-anchor="middle" fill="%23888" font-size="16">Image not available</text></svg>'
                                }}
                              />
                            )}
                          </div>
                          <div className="video-info">
                            {filename.toLowerCase().endsWith('.mp4') ? (
                              <>
                                {data.main_product && (
                                  <div className="info-section">
                                    <h4>Product:</h4>
                                    <p className="analysis-text">{data.main_product}</p>
                                  </div>
                                )}
                                {data.target_age_range && (
                                  <div className="info-section">
                                    <h4>Target Age:</h4>
                                    <p className="analysis-text">{data.target_age_range}</p>
                                  </div>
                                )}
                                {data.length && (
                                  <div className="info-section">
                                    <h4>Length:</h4>
                                    <p className="analysis-text">{data.length}s • {data.aspect_ratio}</p>
                                  </div>
                                )}
                              </>
                            ) : (
                              <>
                                {data.age_demographic && (
                                  <div className="info-section">
                                    <h4>Demographics:</h4>
                                    <p className="analysis-text">{data.age_demographic} • {data.gender_demographic}</p>
                                  </div>
                                )}
                                {data.scene_setting && (
                                  <div className="info-section">
                                    <h4>Scene:</h4>
                                    <p className="analysis-text">{data.scene_setting}</p>
                                  </div>
                                )}
                              </>
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
                    <source src={`http://localhost:8000/datasets/ads/videos/${selectedMedia.filename}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <img
                    src={`http://localhost:8000/datasets/ads/images/${selectedMedia.filename}`}
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

                {selectedMedia.filename.toLowerCase().endsWith('.mp4') ? (
                  /* Video Analysis */
                  <>
                    {selectedMedia.data.main_product && (
                      <div className="analysis-section">
                        <h4>Product & Targeting</h4>
                        <div className="analysis-grid">
                          <div className="analysis-item full-width">
                            <span className="analysis-label">Main Product:</span>
                            <span className="analysis-value">{selectedMedia.data.main_product}</span>
                          </div>
                          <div className="analysis-item">
                            <span className="analysis-label">Target Age:</span>
                            <span className="analysis-value">{selectedMedia.data.target_age_range}</span>
                          </div>
                          <div className="analysis-item">
                            <span className="analysis-label">Target Income:</span>
                            <span className="analysis-value">{selectedMedia.data.target_income_level}</span>
                          </div>
                          {selectedMedia.data.target_geographic_area && selectedMedia.data.target_geographic_area !== 'N/A' && (
                            <div className="analysis-item">
                              <span className="analysis-label">Geographic Area:</span>
                              <span className="analysis-value">{selectedMedia.data.target_geographic_area}</span>
                            </div>
                          )}
                          {selectedMedia.data.target_interests && selectedMedia.data.target_interests.length > 0 && (
                            <div className="analysis-item full-width">
                              <span className="analysis-label">Target Interests:</span>
                              <span className="analysis-value">{selectedMedia.data.target_interests.join(', ')}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    <div className="analysis-section">
                      <h4>Video Details</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Resolution:</span>
                          <span className="analysis-value">{selectedMedia.data.resolution}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Aspect Ratio:</span>
                          <span className="analysis-value">{selectedMedia.data.aspect_ratio}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Length:</span>
                          <span className="analysis-value">{selectedMedia.data.length}s</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Targeting Type:</span>
                          <span className="analysis-value">{selectedMedia.data.targeting_type}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Verbosity:</span>
                          <span className="analysis-value">{selectedMedia.data.verbosity}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Hook Rating:</span>
                          <span className="analysis-value">{selectedMedia.data.hook_rating}/5</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Purchase Urgency:</span>
                          <span className="analysis-value">{selectedMedia.data.purchase_urgency}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Product Visibility:</span>
                          <span className="analysis-value">{selectedMedia.data.product_visibility_score}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Visual Density:</span>
                          <span className="analysis-value">{selectedMedia.data.visual_density}</span>
                        </div>
                      </div>
                    </div>

                    {selectedMedia.data.message_types && selectedMedia.data.message_types.length > 0 && (
                      <div className="analysis-section">
                        <h4>Message Types</h4>
                        <div className="message-types">
                          {selectedMedia.data.message_types.map((type: string, idx: number) => (
                            <span key={idx} className="message-type-badge">{type}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="analysis-section">
                      <h4>Demographics & Style</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Age Demographic:</span>
                          <span className="analysis-value">{selectedMedia.data.age_demographic}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Gender Demographic:</span>
                          <span className="analysis-value">{selectedMedia.data.gender_demographic}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Activity Level:</span>
                          <span className="analysis-value">{selectedMedia.data.activity_level}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Music Intensity:</span>
                          <span className="analysis-value">{selectedMedia.data.music_intensity}</span>
                        </div>
                      </div>
                    </div>

                    <div className="analysis-section">
                      <h4>Emotional Indices (0 to 1.0)</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Fear:</span>
                          <span className={`analysis-value ${(selectedMedia.data.fear_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.fear_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Comfort:</span>
                          <span className={`analysis-value ${(selectedMedia.data.comfort_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.comfort_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Humor:</span>
                          <span className={`analysis-value ${(selectedMedia.data.humor_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.humor_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Success:</span>
                          <span className={`analysis-value ${(selectedMedia.data.success_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.success_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Love:</span>
                          <span className={`analysis-value ${(selectedMedia.data.love_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.love_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Family:</span>
                          <span className={`analysis-value ${(selectedMedia.data.family_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.family_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Adventure:</span>
                          <span className={`analysis-value ${(selectedMedia.data.adventure_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.adventure_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Nostalgia:</span>
                          <span className={`analysis-value ${(selectedMedia.data.nostalgia_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.nostalgia_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Health:</span>
                          <span className={`analysis-value ${(selectedMedia.data.health_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.health_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Luxury:</span>
                          <span className={`analysis-value ${(selectedMedia.data.luxury_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.luxury_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {selectedMedia.data.color_palette && selectedMedia.data.color_palette.length > 0 && (
                      <div className="analysis-section">
                        <h4>Color Palette</h4>
                        <div className="color-palette">
                          {selectedMedia.data.color_palette.map((color: string, idx: number) => (
                            <div key={idx} className="color-swatch">
                              <div className="color-box" style={{ backgroundColor: color }}></div>
                              <span className="color-hex">{color}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedMedia.data.visual_motifs && selectedMedia.data.visual_motifs.length > 0 && (
                      <div className="analysis-section">
                        <h4>Visual Motifs</h4>
                        <div className="analysis-grid">
                          <div className="analysis-item full-width">
                            <span className="analysis-value">{selectedMedia.data.visual_motifs.join(', ')}</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {selectedMedia.data.scene_settings && selectedMedia.data.scene_settings.length > 0 && (
                      <div className="analysis-section">
                        <h4>Scene Settings</h4>
                        <div className="analysis-grid">
                          {selectedMedia.data.scene_settings.map((setting: string, idx: number) => (
                            <div key={idx} className="analysis-item full-width">
                              <span className="analysis-value">{setting}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedMedia.data.scene_cuts && selectedMedia.data.scene_cuts.length > 0 && (
                      <div className="analysis-section">
                        <h4>Scene Cuts</h4>
                        <div className="analysis-grid">
                          <div className="analysis-item full-width">
                            <span className="analysis-value">{selectedMedia.data.scene_cuts.length} cuts at: {selectedMedia.data.scene_cuts.map((t: number) => t.toFixed(2) + 's').join(', ')}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  /* Image Analysis */
                  <>
                    <div className="analysis-section">
                      <h4>Demographics & Characteristics</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Age Demographic:</span>
                          <span className="analysis-value">{selectedMedia.data.age_demographic}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Gender Demographic:</span>
                          <span className="analysis-value">{selectedMedia.data.gender_demographic}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Verbosity:</span>
                          <span className="analysis-value">{selectedMedia.data.verbosity}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Activity:</span>
                          <span className="analysis-value">{selectedMedia.data.activity}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Call to Action:</span>
                          <span className="analysis-value">{selectedMedia.data.call_to_action_level}/5</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Formality:</span>
                          <span className="analysis-value">{selectedMedia.data.formality_level}/5</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Benefit Framing:</span>
                          <span className="analysis-value">{selectedMedia.data.benefit_framing}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Temporal Urgency:</span>
                          <span className="analysis-value">{selectedMedia.data.temporal_urgency_intensity}/5</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Scene Setting:</span>
                          <span className="analysis-value">{selectedMedia.data.scene_setting}</span>
                        </div>
                      </div>
                    </div>

                    <div className="analysis-section">
                      <h4>Emotional Indices (0 to 1.0)</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Fear:</span>
                          <span className={`analysis-value ${(selectedMedia.data.fear_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.fear_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Comfort:</span>
                          <span className={`analysis-value ${(selectedMedia.data.comfort_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.comfort_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Humor:</span>
                          <span className={`analysis-value ${(selectedMedia.data.humor_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.humor_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Success:</span>
                          <span className={`analysis-value ${(selectedMedia.data.success_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.success_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Love:</span>
                          <span className={`analysis-value ${(selectedMedia.data.love_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.love_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Family:</span>
                          <span className={`analysis-value ${(selectedMedia.data.family_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.family_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Adventure:</span>
                          <span className={`analysis-value ${(selectedMedia.data.adventure_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.adventure_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Nostalgia:</span>
                          <span className={`analysis-value ${(selectedMedia.data.nostalgia_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.nostalgia_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Health:</span>
                          <span className={`analysis-value ${(selectedMedia.data.health_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.health_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Luxury:</span>
                          <span className={`analysis-value ${(selectedMedia.data.luxury_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {selectedMedia.data.luxury_index?.toFixed(1) || '0.0'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {selectedMedia.data.color_palette && selectedMedia.data.color_palette.length > 0 && (
                      <div className="analysis-section">
                        <h4>Color Palette</h4>
                        <div className="color-palette">
                          {selectedMedia.data.color_palette.map((color: string, idx: number) => (
                            <div key={idx} className="color-swatch">
                              <div className="color-box" style={{ backgroundColor: color }}></div>
                              <span className="color-hex">{color}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {selectedMedia.data.text && (
                      <div className="analysis-section">
                        <h4>Extracted Text</h4>
                        <div className="analysis-grid">
                          <div className="analysis-item full-width">
                            <span className="analysis-value" style={{ whiteSpace: 'pre-wrap' }}>{selectedMedia.data.text}</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

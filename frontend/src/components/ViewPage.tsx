import { useState, useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { useDatasetAnalysis } from '../hooks/useDatasets'
import type { MediaFile } from '../types/index'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts'

export const ViewPage = () => {
  const { datasetName } = useParams<{ datasetName: string }>()
  const { analysis, loading, error } = useDatasetAnalysis(datasetName)
  const [selectedMedia, setSelectedMedia] = useState<{filename: string, data: any} | null>(null)
  const [searchQuery, setSearchQuery] = useState<string>('')

  // Helper function to prepare emotional indices data for radar chart
  const prepareEmotionalData = (data: any) => {
    return [
      { emotion: 'Fear', value: (data.fear_index || 0) },
      { emotion: 'Comfort', value: (data.comfort_index || 0) },
      { emotion: 'Humor', value: (data.humor_index || 0) },
      { emotion: 'Success', value: (data.success_index || 0) },
      { emotion: 'Love', value: (data.love_index || 0) },
      { emotion: 'Family', value: (data.family_index || 0) },
      { emotion: 'Adventure', value: (data.adventure_index || 0) },
      { emotion: 'Nostalgia', value: (data.nostalgia_index || 0) },
      { emotion: 'Health', value: (data.health_index || 0) },
      { emotion: 'Luxury', value: (data.luxury_index || 0) }
    ]
  }

  // Helper function to detect if timestamps need conversion (have hundredths place decimals)
  const needsTimestampConversion = (sceneCuts: number[]) => {
    return sceneCuts.some(timestamp => {
      const decimalPart = timestamp - Math.floor(timestamp)
      if (decimalPart === 0) return false
      
      // Check if decimal represents hundredths of seconds (e.g., 1.45 = 1 minute 45 seconds)
      // This happens when decimal part has exactly 2 digits or represents values > 0.59
      const decimalStr = decimalPart.toFixed(10) // Get enough precision
      const afterDecimal = decimalStr.split('.')[1]
      
      // Look for patterns like .45, .23, etc. (hundredths that should be seconds)
      return afterDecimal && (afterDecimal.length >= 2) && (decimalPart <= 0.99)
    })
  }

  // Helper function to convert timestamp format from minutes.seconds to total seconds
  const convertTimestampToSeconds = (timestamp: number) => {
    const minutes = Math.floor(timestamp)
    const seconds = (timestamp - minutes) * 100
    return minutes * 60 + seconds
  }

  // Helper function to safely format emotional index values
  const formatEmotionalIndex = (value: any) => {
    return Number(value || 0).toFixed(1)
  }

  // Helper function to collect quality warnings for a media file
  const getMediaWarnings = (data: any, filename: string) => {
    const warnings: string[] = []
    
    if (filename.toLowerCase().endsWith('.mp4')) {
      if (data.video_bitrate_kbps && data.video_bitrate_kbps < 1000) {
        warnings.push(`Low video bitrate: ${data.video_bitrate_kbps} kbps (recommended: 1000+ kbps)`)
      }
      if (data.audio_bitrate_kbps && data.audio_bitrate_kbps < 100) {
        warnings.push(`Low audio bitrate: ${data.audio_bitrate_kbps} kbps (recommended: 100+ kbps)`)
      }
    }
    
    return warnings
  }

  // Helper function to calculate cut frequency over time using sliding window
  const calculateCutFrequency = (sceneCuts: number[], videoLength: number) => {
    if (!sceneCuts || sceneCuts.length === 0) return []
    
    // Check if conversion is needed, then convert and filter
    const processedCuts = needsTimestampConversion(sceneCuts)
      ? sceneCuts.map(convertTimestampToSeconds).filter(cutTime => cutTime > 0)
      : sceneCuts.filter(cutTime => cutTime > 0)
    
    const windowSize = Math.max(3, videoLength / 20) // Sliding window size (adaptive)
    const stepSize = Math.max(0.5, videoLength / 50) // Step size for sampling points
    const frequencyData = []
    
    // Calculate frequency at regular intervals
    for (let time = 0; time <= videoLength; time += stepSize) {
      // Count cuts within the sliding window centered at current time
      const windowStart = Math.max(0, time - windowSize / 2)
      const windowEnd = Math.min(videoLength, time + windowSize / 2)
      
      // Count cuts in this window (using processed timestamps)
      const cutsInWindow = processedCuts.filter(cutTime => 
        cutTime >= windowStart && cutTime <= windowEnd
      ).length
      
      // Calculate frequency as cuts per second in this window
      const windowDuration = windowEnd - windowStart
      const frequency = windowDuration > 0 ? cutsInWindow / windowDuration : 0
      
      frequencyData.push({
        time: parseFloat(time.toFixed(1)),
        frequency: parseFloat((frequency * 60).toFixed(2)), // Convert to cuts per minute for better readability
        cutsInWindow
      })
    }
    
    return frequencyData
  }

  const filteredEntries = useMemo(() => {
    if (!analysis) return []
    
    const query = searchQuery.toLowerCase()
    
    // Semantic mapping for similar terms
    const semanticMap: { [key: string]: string[] } = {
      // Emotions
      'happy': ['joy', 'cheerful', 'positive', 'upbeat', 'smile', 'comfort', 'success'],
      'joy': ['happy', 'cheerful', 'positive', 'upbeat', 'smile', 'comfort', 'success'],
      'sad': ['sorrow', 'depression', 'melancholy', 'down', 'unhappy', 'fear'],
      'fear': ['scary', 'afraid', 'anxious', 'worry', 'concern', 'panic', 'nervous'],
      'love': ['romance', 'affection', 'heart', 'relationship', 'family', 'care'],
      'angry': ['mad', 'rage', 'furious', 'upset', 'irritated'],
      'calm': ['peaceful', 'serene', 'relaxed', 'tranquil', 'comfort', 'soothing'],
      'exciting': ['thrilling', 'adventure', 'energetic', 'dynamic', 'intense'],
      'luxury': ['premium', 'expensive', 'high-end', 'exclusive', 'elite', 'fancy'],
      'health': ['wellness', 'fitness', 'medical', 'doctor', 'exercise', 'nutrition'],
      
      // Demographics
      'young': ['youth', 'teen', 'teenager', 'adolescent', 'millennial', 'gen z'],
      'old': ['senior', 'elderly', 'mature', 'boomer', 'aged'],
      'adult': ['grown-up', 'mature', 'professional', 'working'],
      'male': ['man', 'men', 'masculine', 'guy', 'gentleman'],
      'female': ['woman', 'women', 'feminine', 'lady', 'girl'],
      
      // Activities
      'exercise': ['workout', 'fitness', 'gym', 'training', 'sport'],
      'fitness': ['exercise', 'workout', 'gym', 'training', 'health'],
      'gym': ['fitness', 'exercise', 'workout', 'training'],
      'outdoor': ['outside', 'nature', 'park', 'garden', 'fresh air'],
      'indoor': ['inside', 'interior', 'home', 'office', 'building'],
      
      // Products
      'car': ['vehicle', 'auto', 'automobile', 'truck', 'van'],
      'food': ['meal', 'eating', 'restaurant', 'cuisine', 'nutrition'],
      'tech': ['technology', 'digital', 'computer', 'phone', 'gadget'],
      'clothing': ['fashion', 'apparel', 'wear', 'outfit', 'style']
    }
    
    // Helper function to get related terms
    const getRelatedTerms = (searchTerm: string): string[] => {
      const related: string[] = [searchTerm]
      for (const [key, synonyms] of Object.entries(semanticMap)) {
        if (key.includes(searchTerm) || searchTerm.includes(key)) {
          related.push(...synonyms)
        }
        if (synonyms.some(syn => syn.includes(searchTerm) || searchTerm.includes(syn))) {
          related.push(key, ...synonyms)
        }
      }
      return [...new Set(related)] // Remove duplicates
    }
    
    const relatedTerms = getRelatedTerms(query)
    
    return Object.entries(analysis)
      .filter(([filename, data]) => {
        // Search by filename
        if (filename.toLowerCase().includes(query)) return true
        
        // Helper function to search in array fields with semantic matching
        const searchInArray = (arr: string[] | undefined): boolean => {
          if (!arr) return false
          return arr.some(item => 
            relatedTerms.some(term => item.toLowerCase().includes(term))
          )
        }
        
        // Helper function to search in string fields with semantic matching
        const searchInString = (str: string | undefined): boolean => {
          if (!str) return false
          return relatedTerms.some(term => str.toLowerCase().includes(term))
        }
        
        // Helper function to search emotional indices (for values > 0.5) with semantic matching
        const searchHighEmotion = (emotionName: string, value: number | undefined): boolean => {
          return relatedTerms.some(term => emotionName.toLowerCase().includes(term)) && (value || 0) > 0.5
        }
        
        // Common fields for both images and videos
        if (searchInString(data.text)) return true
        if (searchInString(data.age_demographic)) return true
        if (searchInString(data.gender_demographic)) return true
        if (searchInString(data.scene_setting)) return true
        if (searchInString(data.purchase_urgency)) return true
        if (searchInString(data.visual_density)) return true
        if (searchInArray(data.visual_motifs)) return true
        if (searchInArray(data.color_palette)) return true
        
        // Search emotional indices
        if (searchHighEmotion('fear', data.fear_index)) return true
        if (searchHighEmotion('comfort', data.comfort_index)) return true
        if (searchHighEmotion('humor', data.humor_index)) return true
        if (searchHighEmotion('success', data.success_index)) return true
        if (searchHighEmotion('love', data.love_index)) return true
        if (searchHighEmotion('family', data.family_index)) return true
        if (searchHighEmotion('adventure', data.adventure_index)) return true
        if (searchHighEmotion('nostalgia', data.nostalgia_index)) return true
        if (searchHighEmotion('health', data.health_index)) return true
        if (searchHighEmotion('luxury', data.luxury_index)) return true
        
        // Image-specific fields
        if (filename.toLowerCase().endsWith('.png')) {
          if (searchInString(data.visual_complexity)) return true
          if (searchInString(data.verbosity)) return true
        }
        
        // Video-specific fields
        if (filename.toLowerCase().endsWith('.mp4')) {
          if (searchInString(data.main_product)) return true
          if (searchInString(data.targeting_type)) return true
          if (searchInString(data.target_geographic_area)) return true
          if (searchInArray(data.target_interests)) return true
          if (searchInArray(data.message_types)) return true
          if (searchInString(data.activity_level)) return true
          if (searchInString(data.music_intensity)) return true
          if (searchInArray(data.scene_settings)) return true
        }
        
        return false
      })
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
  }, [analysis, searchQuery])

  if (loading) {
    return (
      <div className="view-page">
        <div className="container">
          <div className="loading-container">
            <p>Loading dataset analysis...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !analysis) {
    return (
      <div className="view-page">
        <div className="container">
          <div className="error-message">
            {error || `No analysis found for dataset: ${datasetName}`}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="view-page">
      <div className="container">
        <h2 className="dataset-title">Dataset: {datasetName}</h2>

        <div className="search-container">
          <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="11" cy="11" r="8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M21 21l-4.35-4.35" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <input
            type="text"
            className="search-input"
            placeholder="Search by name, content, demographics, emotions, products..."
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

        <p className="result-summary">
          Showing {filteredEntries.length} of {Object.keys(analysis).length} files
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
                      <source src={`http://localhost:8000/datasets/${datasetName}/videos/${filename}`} type="video/mp4" />
                      Your browser does not support the video tag.
                    </video>
                  ) : (
                    <img
                      src={`http://localhost:8000/datasets/${datasetName}/images/${filename}`}
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

        {selectedMedia && (
          <div className="modal-overlay" onClick={() => setSelectedMedia(null)}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
              <button className="modal-close" onClick={() => setSelectedMedia(null)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
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
                    <source src={`http://localhost:8000/datasets/${datasetName}/videos/${selectedMedia.filename}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <img
                    src={`http://localhost:8000/datasets/${datasetName}/images/${selectedMedia.filename}`}
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

                {/* Warnings Section */}
                {(() => {
                  const warnings = getMediaWarnings(selectedMedia.data, selectedMedia.filename)
                  return warnings.length > 0 && (
                    <div className="warnings-section">
                      <h4>⚠️ Quality Warnings</h4>
                      <ul className="warnings-list">
                        {warnings.map((warning, index) => (
                          <li key={index} className="warning-item">{warning}</li>
                        ))}
                      </ul>
                    </div>
                  )
                })()}

                {/* Summary Section - DISABLED */}
                {/* {selectedMedia.data.summary && (
                  <div className="summary-section">
                    <h4>📊 Analysis Summary</h4>
                    <p className="summary-text">{selectedMedia.data.summary}</p>
                  </div>
                )} */}

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
                        {selectedMedia.data.video_bitrate_kbps && (
                          <div className="analysis-item">
                            <span className="analysis-label">
                              {selectedMedia.data.video_bitrate_kbps < 1000 ? (
                                <span 
                                  className="warning-icon" 
                                  title="Low video bitrate - may affect quality"
                                >
                                  ⚠️ 
                                </span>
                              ) : ''}Video Bitrate:
                            </span>
                            <span className="analysis-value">{selectedMedia.data.video_bitrate_kbps} kbps</span>
                          </div>
                        )}
                        {selectedMedia.data.audio_bitrate_kbps && (
                          <div className="analysis-item">
                            <span className="analysis-label">
                              {selectedMedia.data.audio_bitrate_kbps < 100 ? (
                                <span 
                                  className="warning-icon" 
                                  title="Low audio bitrate - may affect sound quality"
                                >
                                  ⚠️ 
                                </span>
                              ) : ''}Audio Bitrate:
                            </span>
                            <span className="analysis-value">{selectedMedia.data.audio_bitrate_kbps} kbps</span>
                          </div>
                        )}
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
                      
                      {/* Radar Chart */}
                      <div style={{ width: '100%', height: '300px', margin: '20px 0' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={prepareEmotionalData(selectedMedia.data)}>
                            <PolarGrid stroke="var(--capybara-brown)" />
                            <PolarAngleAxis 
                              dataKey="emotion" 
                              tick={{ 
                                fontSize: 13, 
                                fill: 'var(--dark-roast)', 
                                fontWeight: 600,
                                fontFamily: 'var(--font-primary, system-ui)'
                              }} 
                            />
                            <PolarRadiusAxis 
                              angle={0} 
                              domain={[0, 1]} 
                              tick={{ 
                                fontSize: 11, 
                                fill: 'var(--text-secondary)',
                                fontWeight: 500
                              }}
                              tickCount={6}
                            />
                            <Radar
                              name="Emotional Intensity"
                              dataKey="value"
                              stroke="var(--rosy-cheek)"
                              fill="var(--rosy-cheek)"
                              fillOpacity={0.25}
                              strokeWidth={3}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>

                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Fear:</span>
                          <span className={`analysis-value ${(selectedMedia.data.fear_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.fear_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Comfort:</span>
                          <span className={`analysis-value ${(selectedMedia.data.comfort_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.comfort_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Humor:</span>
                          <span className={`analysis-value ${(selectedMedia.data.humor_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.humor_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Success:</span>
                          <span className={`analysis-value ${(selectedMedia.data.success_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.success_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Love:</span>
                          <span className={`analysis-value ${(selectedMedia.data.love_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.love_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Family:</span>
                          <span className={`analysis-value ${(selectedMedia.data.family_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.family_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Adventure:</span>
                          <span className={`analysis-value ${(selectedMedia.data.adventure_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.adventure_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Nostalgia:</span>
                          <span className={`analysis-value ${(selectedMedia.data.nostalgia_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.nostalgia_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Health:</span>
                          <span className={`analysis-value ${(selectedMedia.data.health_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.health_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Luxury:</span>
                          <span className={`analysis-value ${(selectedMedia.data.luxury_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.luxury_index)}
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
                        
                        {/* Scene Cuts Frequency Over Time Chart */}
                        <div style={{ width: '100%', height: '280px', margin: '20px 0' }}>
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart 
                              data={calculateCutFrequency(selectedMedia.data.scene_cuts, selectedMedia.data.length || 30)}
                              margin={{ top: 20, right: 30, left: 60, bottom: 40 }}
                            >
                              <CartesianGrid strokeDasharray="3 3" stroke="var(--capybara-brown)" opacity={0.3} />
                              <XAxis 
                                dataKey="time" 
                                type="number"
                                scale="linear"
                                domain={['dataMin', 'dataMax']}
                                tick={{ 
                                  fontSize: 11, 
                                  fill: 'var(--text-secondary)',
                                  fontWeight: 500
                                }}
                                label={{ 
                                  value: 'Time (seconds)', 
                                  position: 'insideBottom', 
                                  offset: -10,
                                  style: { textAnchor: 'middle', fill: 'var(--dark-roast)', fontWeight: 600 }
                                }}
                              />
                              <YAxis 
                                tick={{ 
                                  fontSize: 11, 
                                  fill: 'var(--text-secondary)',
                                  fontWeight: 500
                                }}
                                label={{ 
                                  value: 'Cut Frequency (cuts/min)', 
                                  angle: -90, 
                                  position: 'insideLeft',
                                  style: { textAnchor: 'middle', fill: 'var(--dark-roast)', fontWeight: 600 }
                                }}
                              />
                              <Tooltip 
                                contentStyle={{
                                  backgroundColor: 'var(--bg-secondary)',
                                  border: '1px solid var(--border-subtle)',
                                  borderRadius: '8px',
                                  fontSize: '12px',
                                  color: 'var(--text-primary)'
                                }}
                                labelStyle={{ color: 'var(--dark-roast)', fontWeight: 600 }}
                                formatter={(value: number, name: string) => [
                                  `${value} cuts/min`, 'Frequency'
                                ]}
                                labelFormatter={(time: number) => `Time: ${time}s`}
                              />
                              <Line 
                                type="basis"
                                dataKey="frequency" 
                                stroke="var(--data-purple)"
                                strokeWidth={4}
                                dot={false}
                                activeDot={{ 
                                  r: 6, 
                                  fill: 'var(--rosy-cheek)',
                                  stroke: 'var(--data-purple)',
                                  strokeWidth: 3
                                }}
                                connectNulls={false}
                                strokeDasharray="0"
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>

                        <div className="analysis-grid">
                          <div className="analysis-item full-width">
                            <span className="analysis-value">
                              {(() => {
                                const validCuts = needsTimestampConversion(selectedMedia.data.scene_cuts)
                                  ? selectedMedia.data.scene_cuts.map(convertTimestampToSeconds).filter(cutTime => cutTime > 0)
                                  : selectedMedia.data.scene_cuts.filter(cutTime => cutTime > 0)
                                return `${validCuts.length} total cuts at: ${
                                  validCuts.map(cutTime => Math.round(cutTime) + 's').join(', ')
                                }`
                              })()}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  /* Image Analysis */
                  <>
                    <div className="analysis-section">
                      <h4>Visual & Content Analysis</h4>
                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Product Visibility:</span>
                          <span className="analysis-value">{selectedMedia.data.product_visibility_score}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Visual Density:</span>
                          <span className="analysis-value">{selectedMedia.data.visual_density}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Visual Complexity:</span>
                          <span className="analysis-value">{selectedMedia.data.visual_complexity}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Purchase Urgency:</span>
                          <span className="analysis-value">{selectedMedia.data.purchase_urgency}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Verbosity:</span>
                          <span className="analysis-value">{selectedMedia.data.verbosity}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Formality:</span>
                          <span className="analysis-value">{selectedMedia.data.formality_level}/4</span>
                        </div>
                      </div>
                    </div>

                    <div className="analysis-section">
                      <h4>Demographics & Content</h4>
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
                          <span className="analysis-label">Benefit Framing:</span>
                          <span className="analysis-value">{selectedMedia.data.benefit_framing}</span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Scene Setting:</span>
                          <span className="analysis-value">{selectedMedia.data.scene_setting}</span>
                        </div>
                      </div>
                    </div>

                    <div className="analysis-section">
                      <h4>Emotional Indices (0 to 1.0)</h4>
                      
                      {/* Radar Chart */}
                      <div style={{ width: '100%', height: '300px', margin: '20px 0' }}>
                        <ResponsiveContainer width="100%" height="100%">
                          <RadarChart data={prepareEmotionalData(selectedMedia.data)}>
                            <PolarGrid stroke="var(--capybara-brown)" />
                            <PolarAngleAxis 
                              dataKey="emotion" 
                              tick={{ 
                                fontSize: 13, 
                                fill: 'var(--dark-roast)', 
                                fontWeight: 600,
                                fontFamily: 'var(--font-primary, system-ui)'
                              }} 
                            />
                            <PolarRadiusAxis 
                              angle={0} 
                              domain={[0, 1]} 
                              tick={{ 
                                fontSize: 11, 
                                fill: 'var(--text-secondary)',
                                fontWeight: 500
                              }}
                              tickCount={6}
                            />
                            <Radar
                              name="Emotional Intensity"
                              dataKey="value"
                              stroke="var(--rosy-cheek)"
                              fill="var(--rosy-cheek)"
                              fillOpacity={0.25}
                              strokeWidth={3}
                            />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>

                      <div className="analysis-grid">
                        <div className="analysis-item">
                          <span className="analysis-label">Fear:</span>
                          <span className={`analysis-value ${(selectedMedia.data.fear_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.fear_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Comfort:</span>
                          <span className={`analysis-value ${(selectedMedia.data.comfort_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.comfort_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Humor:</span>
                          <span className={`analysis-value ${(selectedMedia.data.humor_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.humor_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Success:</span>
                          <span className={`analysis-value ${(selectedMedia.data.success_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.success_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Love:</span>
                          <span className={`analysis-value ${(selectedMedia.data.love_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.love_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Family:</span>
                          <span className={`analysis-value ${(selectedMedia.data.family_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.family_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Adventure:</span>
                          <span className={`analysis-value ${(selectedMedia.data.adventure_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.adventure_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Nostalgia:</span>
                          <span className={`analysis-value ${(selectedMedia.data.nostalgia_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.nostalgia_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Health:</span>
                          <span className={`analysis-value ${(selectedMedia.data.health_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.health_index)}
                          </span>
                        </div>
                        <div className="analysis-item">
                          <span className="analysis-label">Luxury:</span>
                          <span className={`analysis-value ${(selectedMedia.data.luxury_index || 0) > 0.5 ? 'high-emotion' : ''}`}>
                            {formatEmotionalIndex(selectedMedia.data.luxury_index)}
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
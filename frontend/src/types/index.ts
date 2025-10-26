export interface Dataset {
  name: string
  has_analysis: boolean
  files: string[]
}

export interface MediaFile {
  filename: string
  data: {
    // Common fields
    metadata?: {
      width: number
      height: number
      resolution: string
      format: string
    }
    
    // Image analysis fields
    product_visibility_score?: string
    visual_density?: string
    visual_complexity?: string
    purchase_urgency?: string
    verbosity?: string
    formality_level?: number
    benefit_framing?: string
    age_demographic?: string
    gender_demographic?: string
    scene_setting?: string
    
    // Video analysis fields
    main_product?: string
    targeting_type?: string
    target_age_range?: string
    target_income_level?: string
    target_geographic_area?: string
    target_interests?: string[]
    hook_rating?: number
    message_types?: string[]
    activity_level?: string
    music_intensity?: string
    length?: number
    aspect_ratio?: string
    resolution?: string
    video_bitrate_kbps?: number
    audio_bitrate_kbps?: number
    
    // Emotional indices (both)
    fear_index?: number
    comfort_index?: number
    humor_index?: number
    success_index?: number
    love_index?: number
    family_index?: number
    adventure_index?: number
    nostalgia_index?: number
    health_index?: number
    luxury_index?: number
    
    // Other fields
    color_palette?: string[]
    text?: string
    visual_motifs?: string[]
    scene_settings?: string[]
    scene_cuts?: number[]
    analysis_error?: string
  }
}

export interface DatasetAnalysis {
  [filename: string]: MediaFile['data']
}
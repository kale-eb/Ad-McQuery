import json
import os
from typing import Dict, Any, List
from video_preprocessing import preprocess_video
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()


class VideoAnalysis(BaseModel):
    targeting_type: str  # "first_impression" or "retargeting"
    comprehension_rating: int  # 1-5
    target_age_range: str  # e.g. "18-25", "25-35", etc.
    target_income_level: str  # "low", "middle", "high", or "mixed"
    target_geographic_area: str  # "urban", "suburban", "rural", or "universal"
    target_interests: List[str]  # list of customer interests
    hook_rating: int  # 1-5
    conversion_focused: bool  # true/false


def analyze_video_with_gemini(video_data: Dict[str, Any], video_path: str) -> Dict[str, Any]:
    """
    Analyze video using Gemini 2.5 Flash API for advanced metrics.
    
    Args:
        video_data: Preprocessed video data containing resolution, aspect_ratio, length, whisper_transcript
        video_path: Path to the video file for Gemini to analyze
    
    Returns:
        Complete analysis including preprocessing data + Gemini analysis
    """
    import google.generativeai as genai
    
    # Configure Gemini API
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Extract transcript text for analysis
    full_text = video_data['whisper_transcript']['full_text']
    video_length = video_data['length']
    
    # Create analysis prompt
    prompt = f"""
Analyze this video advertisement objectively for targeting and marketing effectiveness. 
Please analyze and provide the following metrics in JSON format:

{{
    "targeting_type": "first_impression" or "retargeting",
    "comprehension_rating": 1-5 (how easy to understand),
    "target_age_range": "specific age range like 18-25, 25-35, 35-50, 50+",
    "target_income_level": "specific income level",
    "target_geographic_area": "specific geographic type that the ad targets (such as 'X county, East Coast US'),
    "target_interests": ["list", "of", "customer", "interests", "(up to 3)"],
    "hook_rating": 1-5 (how engaging are first few seconds either visually or verbally),
    "conversion_focused": true/false (direct CTA vs general brand awareness)
}}

ANALYSIS CRITERIA:
- targeting_type: "first_impression" if introducing brand/product, "retargeting" if assumes familiarity
- comprehension_rating: 1=requires the viewer to really think to understand the message, 5=crystal clear message, even a toddler could understand.
- target_age_range: infer from language, references, visual style
- target_income_level: infer from product type, pricing cues, lifestyle depicted
- target_geographic_area: infer from product, explicit mentions, setting, cultural references
- target_interests: what hobbies/interests would this customer have
- hook_rating: 1=non-engaging start, 5=EXTREMELY gripping/interesting (stunt occurs, something unexpected happens, etc.). Remember the AVERAGE video is a 2.5
- conversion_focused: true if has clear IMMEDIATE call-to-action (download, buy now, etc.), false if just building awareness (x product is good).

Be objective and analytical. Base conclusions on concrete evidence from the transcript and metadata.
"""
    
    try:
        # Read video file as base64
        import base64
        with open(video_path, 'rb') as f:
            video_bytes = f.read()
        
        # Get Gemini analysis with structured output
        video_part = {
            "mime_type": "video/mp4",
            "data": base64.b64encode(video_bytes).decode('utf-8')
        }
        
        response = model.generate_content(
            [video_part, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=VideoAnalysis
            )
        )
        
        # Parse JSON response  
        analysis_text = response.text.strip()
        if analysis_text.startswith('```json'):
            analysis_text = analysis_text.replace('```json', '').replace('```', '').strip()
        
        gemini_analysis = json.loads(analysis_text)
        
        # Combine preprocessing data with Gemini analysis
        complete_analysis = {
            # Preprocessing data
            "resolution": video_data["resolution"],
            "aspect_ratio": video_data["aspect_ratio"],
            "length": video_data["length"],
            "video_bitrate_kbps": video_data.get("video_bitrate_kbps"),
            "audio_bitrate_kbps": video_data.get("audio_bitrate_kbps"),
            "full_text_transcript": video_data["whisper_transcript"],
            
            # Gemini analysis (structured)
            "targeting_type": gemini_analysis.get("targeting_type"),
            "comprehension_rating": gemini_analysis.get("comprehension_rating"),
            "target_age_range": gemini_analysis.get("target_age_range"),
            "target_income_level": gemini_analysis.get("target_income_level"),
            "target_geographic_area": gemini_analysis.get("target_geographic_area"),
            "target_interests": gemini_analysis.get("target_interests", []),
            "hook_rating": gemini_analysis.get("hook_rating"),
            "conversion_focused": gemini_analysis.get("conversion_focused")
        }
        
        return complete_analysis
        
    except Exception as e:
        return {
            **video_data,
            "error": f"Gemini API error: {e}"
        }


def analyze_single_video(video_path: str) -> Dict[str, Any]:
    """
    Complete video analysis pipeline: preprocessing + Gemini analysis.
    
    Args:
        video_path: Path to video file
    
    Returns:
        Complete analysis dictionary
    """
    # Check for required API keys
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable not set")
    if not os.environ.get("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    print(f"Analyzing video: {video_path}")
    
    # Step 1: Preprocess video (extract metadata + transcript)
    print("Step 1: Extracting video metadata and transcript...")
    video_data = preprocess_video(video_path)
    
    # Step 2: Analyze with Gemini
    print("Step 2: Analyzing with Gemini 2.5 Flash...")
    complete_analysis = analyze_video_with_gemini(video_data, video_path)
    
    print("Analysis complete!")
    return complete_analysis


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python video_analysis.py <video_path> [output_json_path]")
        print("\nThis script will:")
        print("  1. Extract video metadata and transcript (OpenAI Whisper)")
        print("  2. Analyze targeting and effectiveness (Gemini 2.5 Flash)")
        print("  3. Return complete structured analysis")
        print("\nRequires:")
        print("  - OPENAI_API_KEY environment variable")
        print("  - GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Analyze video
        results = analyze_single_video(video_path)
        
        # Optionally save to JSON
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {output_path}")
        
        # Print summary
        print("\n=== Analysis Summary ===")
        if "error" not in results:
            print(f"Resolution: {results['resolution']}")
            print(f"Length: {results['length']} seconds")
            print(f"Video Bitrate: {results['video_bitrate_kbps']} kbps" if results.get('video_bitrate_kbps') else "Video Bitrate: N/A")
            print(f"Audio Bitrate: {results['audio_bitrate_kbps']} kbps" if results.get('audio_bitrate_kbps') else "Audio Bitrate: N/A")
            print(f"Targeting: {results['targeting_type']}")
            print(f"Target Age: {results['target_age_range']}")
            print(f"Hook Rating: {results['hook_rating']}/5")
            print(f"Conversion Focused: {results['conversion_focused']}")
        else:
            print(f"Error: {results['error']}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)